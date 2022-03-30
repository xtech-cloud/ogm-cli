template_go_mod = r"""module {{org}}-{{service}}

go 1.16

require (
    github.com/asim/go-micro/plugins/config/encoder/yaml/v3 v3.7.0
    github.com/asim/go-micro/plugins/config/source/etcd/v3 v3.7.0
    github.com/asim/go-micro/plugins/logger/logrus/v3 v3.7.0
    github.com/asim/go-micro/plugins/registry/etcd/v3 v3.7.0
    github.com/asim/go-micro/plugins/server/grpc/v3 v3.7.0
    github.com/asim/go-micro/v3 v3.7.0
    github.com/satori/go.uuid v1.2.0
    github.com/sirupsen/logrus v1.8.1
    github.com/xtech-cloud/{{org}}-msp-{{service}} v3.0.0+incompatible
    gopkg.in/yaml.v2 v2.4.0
    gorm.io/driver/mysql v1.1.3
    gorm.io/driver/sqlite v1.2.3
    gorm.io/gorm v1.22.2
)
"""

template_plugin = r"""package main

import (
    _ "github.com/asim/go-micro/plugins/registry/etcd/v3"
)
"""

template_version = r"""package main

var (
    BuildVersion string
    BuildTime    string
    CommitID     string
)
"""

template_makefile = r"""
APP_NAME        := {{org}}-{{service}}
BUILD_VERSION   := $(shell git tag --contains)
BUILD_TIME      := $(shell date "+%F %T")
COMMIT_SHA1     := $(shell git rev-parse HEAD )

.PHONY: build
build:
    go build -ldflags \
        "\
        -X 'main.BuildVersion=${BUILD_VERSION}' \
        -X 'main.BuildTime=${BUILD_TIME}' \
        -X 'main.CommitID=${COMMIT_SHA1}' \
        "\
        -o ./bin/${APP_NAME}

.PHONY: run
run:
    ./bin/${APP_NAME}

.PHONY: install
install:
    go install

.PHONY: clean
clean:
    rm -rf /tmp/{{org}}-{{service}}.db

.PHONY: call
call:
    gomu --registry=etcd --client=grpc call xtc.{{org}}.{{service}} Healthy.Echo '{"msg":"hello"}'

.PHONY: post
post:
    curl -X POST -d '{"msg":"hello"}' localhost/{{org}}/{{service}}/Healthy/Echo                                                                                     1

.PHONY: dist
dist:
    mkdir dist
    tar -zcf dist/${APP_NAME}-${BUILD_VERSION}.tar.gz ./bin/${APP_NAME}

.PHONY: docker
    docker:
    docker build -t xtechcloud/${APP_NAME}:${BUILD_VERSION} .
    docker rm -f ${APP_NAME}
    docker run --restart=always --name=${APP_NAME} --net=host -v /data/${APP_NAME}:/{{org}} -e MSA_REGISTRY_ADDRESS='localhost:2379' -e MSA_CONFIG_DEFINE='{"source":"file","prefix":"/{{org}}/config","key":"${APP_NAME}.yaml"}' -d xtechcloud/${APP_NAME}:${BUILD_VERSION} 
    docker logs -f ${APP_NAME}
"""

template_config_default = r"""package config

const defaultYAML string = `
service:
    name: xtc.{{org}}.{{service}}
    address: :18899
    ttl: 15
    interval: 10
logger:
    level: info
    dir: /var/log/{{org}}/
database:
    # 驱动类型，可选值为 [sqlite,mysql]
    driver: sqlite
    mysql:
        address: localhost:3306
        user: root
        password: mysql@XTC
        db: {{org}}
        # Set the maximum number of connections in the idle connection pool.
        # If MaxOpenConns is greater than 0 but less than the new MaxIdleConns, then the new MaxIdleConns will be reduced to match the MaxOpenConns limit.
        # If n <= 0, no idle connections are retained.
        maxIdleConns: 10
        # Sets the maximum number of open connections to the database.
        # If MaxIdleConns is greater than 0 and the new MaxOpenConns is less than MaxIdleConns, then MaxIdleConns will be reduced to match the new MaxOpenConns limit.
        # If n <= 0, then there is no limit on the number of open connections. The default is 0 (unlimited).
        maxOpenConns: 100
        # Set the maximum amount of time a connection may be reused(Minute).
        # Expired connections may be closed lazily before reuse.
        # If d <= 0, connections are not closed due to a connection's age.
        maxLiftTime: 60
        # Set the maximum amount of time a connection may be idle(Minute).
        # Expired connections may be closed lazily before reuse.
        # If d <= 0, connections are not closed due to a connection's idle time.
        maxIdleTime: 60
    sqlite:
        path: /tmp/{{org}}-{{service}}.db
`
"""

template_config_schema = r"""package config

type Service_ struct {
	Name     string `yaml:name`
	TTL      int64  `yaml:ttl`
	Interval int64  `yaml:interval`
	Address  string `yaml:address`
}

type Logger_ struct {
	Level string `yaml:level`
	Dir   string `yaml:dir`
}

type ConfigSchema_ struct {
	Service  Service_  `yaml:service`
	Logger   Logger_   `yaml:logger`
	Database Database_ `yaml:database`
}

type SQLite_ struct {
	Path string `yaml:path`
}

type MySQL_ struct {
	Address      string `yaml:address`
	User         string `yaml:user`
	Password     string `yaml:password`
	DB           string `yaml:db`
	MaxIdleTime  int    `yaml:maxIdelTime`
	MaxLifeTime  int    `yaml:maxLifeTime`
	MaxIdleConns int    `yaml:maxIdleConns`
	MaxOpenConns int    `yaml:maxOpenConns`
}

type Database_ struct {
	Driver string  `yaml:driver`
	MySQL  MySQL_  `yaml:mysql`
	SQLite SQLite_ `yaml:sqlite`
}
"""

template_config_source = r"""package config

import (
	"encoding/json"
	"fmt"
	"os"
	"strings"

	"github.com/asim/go-micro/plugins/config/encoder/yaml/v3"
	"github.com/asim/go-micro/plugins/config/source/etcd/v3"
	logrusPlugin "github.com/asim/go-micro/plugins/logger/logrus/v3"
	"github.com/asim/go-micro/v3/config"
	"github.com/asim/go-micro/v3/config/reader"
	jsonReader "github.com/asim/go-micro/v3/config/reader/json"
	"github.com/asim/go-micro/v3/config/source"
	"github.com/asim/go-micro/v3/config/source/file"
	"github.com/asim/go-micro/v3/config/source/memory"
	"github.com/asim/go-micro/v3/logger"
	"github.com/sirupsen/logrus"
	goYAML "gopkg.in/yaml.v2"
)

type ConfigDefine struct {
	Source  string `json:source`
	Prefix  string `json:prefix`
	Key     string `json:key`
	Address string
}

var configDefine ConfigDefine

var Schema ConfigSchema_

func setupEnvironment() {
	//registry plugin
	registryPlugin := os.Getenv("MSA_REGISTRY_PLUGIN")
	if "" == registryPlugin {
		registryPlugin = "etcd"
	}
	logger.Infof("MSA_REGISTRY_PLUGIN is %v", registryPlugin)
	os.Setenv("MICRO_REGISTRY", registryPlugin)

	//registry address
	registryAddress := os.Getenv("MSA_REGISTRY_ADDRESS")
	if "" == registryAddress {
		registryAddress = "localhost:2379"
	}
	logger.Infof("MSA_REGISTRY_ADDRESS is %v", registryAddress)
	os.Setenv("MICRO_REGISTRY_ADDRESS", registryAddress)

	//config
	envConfigDefine := os.Getenv("MSA_CONFIG_DEFINE")

	if "" == envConfigDefine {
		logger.Warn("MSA_CONFIG_DEFINE is empty")
		return
	}

	logger.Infof("MSA_CONFIG_DEFINE is %v", envConfigDefine)
	err := json.Unmarshal([]byte(envConfigDefine), &configDefine)
	if err != nil {
		logger.Error(err)
	}
	configDefine.Address = registryAddress
}

func mergeFile(_config config.Config) {
	prefix := configDefine.Prefix
	if !strings.HasSuffix(prefix, "/") {
		prefix = prefix + "/"
	}
	filepath := prefix + configDefine.Key
	fileSource := file.NewSource(
		file.WithPath(filepath),
	)
	err := _config.Load(fileSource)
	if nil != err {
		panic(fmt.Sprintf("load config %v failed: %v", filepath, err))
	}
	err = _config.Scan(&Schema)
	if nil != err {
		panic(fmt.Sprintf("scan config %v failed: %v", filepath, err))
	}
	logger.Infof("load config %v success", filepath)
}

func mergeEtcd(_config config.Config) {
	prefix := configDefine.Prefix
	if !strings.HasSuffix(prefix, "/") {
		prefix = prefix + "/"
	}
	etcdKey := prefix + configDefine.Key
	etcdSource := etcd.NewSource(
		source.WithEncoder(yaml.NewEncoder()),
		etcd.WithAddress(configDefine.Address),
		etcd.WithPrefix(etcdKey),
		etcd.StripPrefix(true),
	)
	err := _config.Load(etcdSource)
	if nil != err {
		panic(fmt.Sprintf("load config %v from etcd failed: %v", etcdKey, err))
	}
	err = _config.Scan(&Schema)
	if nil != err {
		panic(fmt.Sprintf("load config %v from etcd failed: %v", etcdKey, err))
	}
	logger.Infof("load config %v from etcd success", etcdKey)
}

func mergeDefault(_config config.Config) {
	memorySource := memory.NewSource(
		memory.WithYAML([]byte(defaultYAML)),
	)

	err := _config.Load(memorySource)
	if nil != err {
		panic(fmt.Sprintf("load config default failed: %v", err))
	}
	err = _config.Scan(&Schema)
	if nil != err {
		panic(fmt.Sprintf("load config default failed: %v", err))
	}
	logger.Infof("load config default success")
}

func Setup() {
	mode := os.Getenv("MSA_MODE")
	if "" == mode {
		mode = "debug"
	}

	// initialize logger
	if "debug" == mode {
		logger.DefaultLogger = logrusPlugin.NewLogger(
			logger.WithOutput(os.Stdout),
			logger.WithLevel(logger.TraceLevel),
			logrusPlugin.WithTextTextFormatter(new(logrus.TextFormatter)),
		)
		logger.Info("-------------------------------------------------------------")
		logger.Info("- Micro Service Agent -> Setup")
		logger.Info("-------------------------------------------------------------")
		logger.Warn("Running in \"debug\" mode. Switch to \"release\" mode in production.")
		logger.Warn("- using env:   export MSA_MODE=release")
	} else {
		logger.DefaultLogger = logrusPlugin.NewLogger(
			logger.WithOutput(os.Stdout),
			logger.WithLevel(logger.TraceLevel),
			logrusPlugin.WithJSONFormatter(new(logrus.JSONFormatter)),
		)
		logger.Info("-------------------------------------------------------------")
		logger.Info("- Micro Service Agent -> Setup")
		logger.Info("-------------------------------------------------------------")
	}

	conf, err := config.NewConfig(
		config.WithReader(jsonReader.NewReader(reader.WithEncoder(yaml.NewEncoder()))),
	)
	if nil != err {
		panic(err)
	}

	setupEnvironment()

	// load default config
	logger.Tracef("default config is: \n\r%v", defaultYAML)

	// merge others
	if "file" == configDefine.Source {
		mergeFile(conf)
	} else if "etcd" == configDefine.Source {
		mergeEtcd(conf)
	} else {
		mergeDefault(conf)
	}

	ycd, err := goYAML.Marshal(&Schema)
	if nil != err {
		logger.Error(err)
	} else {
		logger.Tracef("current config is: \n\r%v", string(ycd))
	}

	level, err := logger.GetLevel(Schema.Logger.Level)
	if nil != err {
		logger.Warnf("the level %v is invalid, just use info level", Schema.Logger.Level)
		level = logger.InfoLevel
	}

	if "debug" == mode {
		logger.Warn("Using \"MSA_DEBUG_LOG_LEVEL\" to switch log's level in \"debug\" mode.")
		logger.Warn("- using env:   export MSA_DEBUG_LOG_LEVEL=debug")
		debugLogLevel := os.Getenv("MSA_DEBUG_LOG_LEVEL")
		if "" == debugLogLevel {
			debugLogLevel = "trace"
		}
		level, _ = logger.GetLevel(debugLogLevel)
	}
	logger.Infof("level is %v now", level)
	logger.Init(
		logger.WithLevel(level),
	)
}
"""

template_model_db = r"""package model

import (
	"crypto/md5"
	"encoding/base64"
	"encoding/hex"
	"fmt"
	"{{org}}-{{service}}/config"
	"time"

	"github.com/asim/go-micro/v3/logger"
	uuid "github.com/satori/go.uuid"
	"gorm.io/driver/mysql"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

var base64Coder = base64.NewEncoding("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_")

type Conn struct {
	DB *gorm.DB
}

var DefaultConn *Conn

func Setup() {
	var err error
	var db *gorm.DB

	if "sqlite" == config.Schema.Database.Driver {
		dsn := config.Schema.Database.SQLite.Path
		logger.Warnf("!!! Database is lite mode, file at %v", dsn)
		db, err = gorm.Open(sqlite.Open(dsn), &gorm.Config{})
	} else if "mysql" == config.Schema.Database.Driver {
		mysql_addr := config.Schema.Database.MySQL.Address
		mysql_user := config.Schema.Database.MySQL.User
		mysql_passwd := config.Schema.Database.MySQL.Password
		mysql_db := config.Schema.Database.MySQL.DB
		dsn := fmt.Sprintf("%s:%s@tcp(%s)/%s?charset=utf8&parseTime=True", mysql_user, mysql_passwd, mysql_addr, mysql_db)
		db, err = gorm.Open(mysql.Open(dsn), &gorm.Config{})
		sqlDB, err := db.DB()
		if nil != err {
			panic(err)
		}
		sqlDB.SetConnMaxIdleTime(time.Minute * time.Duration(config.Schema.Database.MySQL.MaxIdleTime))
		sqlDB.SetConnMaxLifetime(time.Minute * time.Duration(config.Schema.Database.MySQL.MaxLifeTime))
		sqlDB.SetMaxIdleConns(config.Schema.Database.MySQL.MaxIdleConns)
		sqlDB.SetMaxOpenConns(config.Schema.Database.MySQL.MaxOpenConns)

	} else {
		panic("the driver of database is missing")
	}

	if nil != err {
		logger.Fatal(err)
	}
	DefaultConn = &Conn{
		DB: db,
	}
}

func Cancel() {
}

func AutoMigrateDatabase() {
    var err error
{{migrate_block}}
}

func NewUUID() string {
	guid := uuid.NewV4()
	h := md5.New()
	h.Write(guid.Bytes())
	return hex.EncodeToString(h.Sum(nil))
}

func ToUUID(_content string) string {
	h := md5.New()
	h.Write([]byte(_content))
	return hex.EncodeToString(h.Sum(nil))
}

func MD5(_content string) string {
	h := md5.New()
	h.Write([]byte(_content))
	return hex.EncodeToString(h.Sum(nil))
}

func ToBase64(_content []byte) string {
	return base64Coder.EncodeToString(_content)
}

"""

template_model_migrate_block = r"""
	err = DefaultConn.DB.AutoMigrate(&{{rpc_service}}{})
	if nil != err {
		logger.Fatal(err)
	}
"""

template_model_service = r"""package model

import (
	"time"
    "gorm.io/gorm/clause"
)

type {{rpc_service}} struct {
	UUID      string `gorm:"column:uuid;type:char(32);not null;unique;primaryKey"`
	CreatedAt time.Time
	UpdatedAt time.Time
}


func ({{rpc_service}}) TableName() string {
	return "{{org}}_{{service}}_{{rpc_service}}"
}

type {{rpc_service}}DAO struct {
	conn *Conn
}

func New{{rpc_service}}DAO(_conn *Conn) *{{rpc_service}}DAO {
	conn := DefaultConn
	if nil != _conn {
		conn = _conn
	}
	return &{{rpc_service}}DAO{
		conn: conn,
	}
}

func (this *{{rpc_service}}DAO) Count() (int64, error) {
	var count int64
	err := this.conn.DB.Model(&{{rpc_service}}{}).Count(&count).Error
	return count, err
}

func (this *{{rpc_service}}DAO) Insert(_entity *{{rpc_service}}) error {
	return this.conn.DB.Create(_entity).Error
}

func (this *{{rpc_service}}DAO) Update(_entity *{{rpc_service}}) error {
    // 只更新非零值
	return this.conn.DB.Updates(_entity).Error
}

func (this *{{rpc_service}}DAO) Upsert(_entity *{{rpc_service}}) error {
    // 在冲突时，更新除主键以外的所有列到新值。
    err := this.conn.DB.Clauses(clause.OnConflict{
        UpdateAll: true,
    }).Create(_entity).Error
    return err
}

func (this *{{rpc_service}}DAO) Get(_uuid string) (*{{rpc_service}}, error) {
    var entity {{rpc_service}}
    err := this.conn.DB.Where("uuid = ?", _uuid).First(&entity).Error
    return &entity, err
}

func (this *{{rpc_service}}DAO) List(_offset int64, _count int64) (int64, []*{{rpc_service}}, error) {
	var entityAry []*{{rpc_service}}
    count := int64(0)
	db := this.conn.DB.Model(&{{rpc_service}}{})
    // db = db.Where("key = ?", value)
    if err := db.Count(&count).Error; nil != err {
        return 0, nil, err
    }
    db = db.Offset(int(_offset)).Limit(int(_count)).Order("created_at desc")
	res := db.Find(&entityAry)
	return count, entityAry, res.Error
}

func (this *{{rpc_service}}DAO) Delete(_uuid string) error {
	return this.conn.DB.Where("uuid = ?", _uuid).Delete(&{{rpc_service}}{}).Error
}
"""

template_handler_healthy = r"""
package handler

import (
	"context"

    "github.com/asim/go-micro/v3/logger"

	proto "github.com/xtech-cloud/{{org}}-msp-{{service}}/proto/{{service}}"
)

type Healthy struct{}

func (this *Healthy) Echo(_ctx context.Context, _req *proto.EchoRequest, _rsp *proto.EchoResponse) error {
	logger.Infof("Received Healthy.Echo, msg is %v", _req.Msg)

	_rsp.Msg = _req.Msg

	return nil
}
"""

template_handler_service = r"""package handler

import (
	"context"
	"{{org}}-{{service}}/model"

    "github.com/asim/go-micro/v3/logger"
	proto "github.com/xtech-cloud/{{org}}-msp-{{service}}/proto/{{service}}"
)

type {{rpc_service}} struct{}

{{method_block}}

"""

template_handler_method_block = r"""
func (this *{{rpc_service}}) {{rpc_method}}(_ctx context.Context, _req *proto.{{rpc_req}}, _rsp *proto.{{rpc_rsp}}) error {
	logger.Infof("Received {{rpc_service}}.{{rpc_method}}, req is %v", _req)
	_rsp.Status = &proto.Status{}

    dao := model.New{{rpc_service}}DAO(nil)
    _, err := dao.Count()
    if nil != err {
        _rsp.Status.Code = -1
        _rsp.Status.Message = err.Error()
        return nil
    }

	return nil
} 
"""

template_main = r"""package main

import (
	"crypto/md5"
	"encoding/hex"
	"io"
	"{{org}}-{{service}}/config"
	"{{org}}-{{service}}/handler"
	"{{org}}-{{service}}/model"
	"os"
	"path/filepath"
	"time"

    "github.com/asim/go-micro/v3"
    "github.com/asim/go-micro/v3/logger"
    "github.com/asim/go-micro/plugins/server/grpc/v3"
	proto "github.com/xtech-cloud/{{org}}-msp-{{service}}/proto/{{service}}"
)

func main() {
	config.Setup()
	model.Setup()
    defer model.Cancel()
	model.AutoMigrateDatabase()

	// New Service
	service := micro.NewService(
        micro.Server(grpc.NewServer()),
		micro.Name(config.Schema.Service.Name),
		micro.Version(BuildVersion),
		micro.RegisterTTL(time.Second*time.Duration(config.Schema.Service.TTL)),
		micro.RegisterInterval(time.Second*time.Duration(config.Schema.Service.Interval)),
		micro.Address(config.Schema.Service.Address),
	)

	// Initialise service
	service.Init()

	// Register Handler
	proto.RegisterHealthyHandler(service.Server(), new(handler.Healthy))
{{handler_block}}

	app, _ := filepath.Abs(os.Args[0])

	logger.Info("-------------------------------------------------------------")
	logger.Info("- Micro Service Agent -> Run")
	logger.Info("-------------------------------------------------------------")
	logger.Infof("- version      : %s", BuildVersion)
	logger.Infof("- application  : %s", app)
	logger.Infof("- md5          : %s", md5hex(app))
	logger.Infof("- build        : %s", BuildTime)
	logger.Infof("- commit       : %s", CommitID)
	logger.Info("-------------------------------------------------------------")
	// Run service
	if err := service.Run(); err != nil {
		logger.Error(err)
	}
}

func md5hex(_file string) string {
	h := md5.New()

	f, err := os.Open(_file)
	if err != nil {
		return ""
	}
	defer f.Close()

	io.Copy(h, f)

	return hex.EncodeToString(h.Sum(nil))
}
"""

template_main_handler_block = r"""
	proto.Register{{rpc_service}}Handler(service.Server(), new(handler.{{rpc_service}}))
"""
