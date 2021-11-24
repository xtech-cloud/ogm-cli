template_gitignore = r"""
.vs/
app/bin/
app/obj/
bridge/bin/
bridge/obj/
module/bin/
module/obj/
wpf/bin/
wpf/obj/
*.user
"""

template_sln = r"""
Microsoft Visual Studio Solution File, Format Version 12.00
# Visual Studio Version 16
VisualStudioVersion = 16.0.31112.23
MinimumVisualStudioVersion = 10.0.40219.1
Project("{9A19103F-16F7-4668-BE54-9A1E7A4F7556}") = "app", "app\app.csproj", "{F2F84FF1-7987-476F-8F03-8316DB67217F}"
EndProject
Project("{9A19103F-16F7-4668-BE54-9A1E7A4F7556}") = "module", "module\module.csproj", "{124ACB03-D1AC-479D-B95A-DE9F13C266FA}"
EndProject
Project("{9A19103F-16F7-4668-BE54-9A1E7A4F7556}") = "wpf", "wpf\wpf.csproj", "{ECEBC9A0-5079-470A-A380-5B80756DEA61}"
EndProject
Project("{9A19103F-16F7-4668-BE54-9A1E7A4F7556}") = "bridge", "bridge\bridge.csproj", "{8DF06770-ADA4-407D-ABAF-6C222C73962E}"
EndProject
Global
        GlobalSection(SolutionConfigurationPlatforms) = preSolution
                Debug|Any CPU = Debug|Any CPU
                Release|Any CPU = Release|Any CPU
        EndGlobalSection
        GlobalSection(ProjectConfigurationPlatforms) = postSolution
                {124ACB03-D1AC-479D-B95A-DE9F13C266FA}.Debug|Any CPU.ActiveCfg = Debug|Any CPU
                {124ACB03-D1AC-479D-B95A-DE9F13C266FA}.Debug|Any CPU.Build.0 = Debug|Any CPU
                {124ACB03-D1AC-479D-B95A-DE9F13C266FA}.Release|Any CPU.ActiveCfg = Release|Any CPU
                {124ACB03-D1AC-479D-B95A-DE9F13C266FA}.Release|Any CPU.Build.0 = Release|Any CPU
                {F2F84FF1-7987-476F-8F03-8316DB67217F}.Debug|Any CPU.ActiveCfg = Debug|Any CPU
                {F2F84FF1-7987-476F-8F03-8316DB67217F}.Debug|Any CPU.Build.0 = Debug|Any CPU
                {F2F84FF1-7987-476F-8F03-8316DB67217F}.Release|Any CPU.ActiveCfg = Release|Any CPU
                {F2F84FF1-7987-476F-8F03-8316DB67217F}.Release|Any CPU.Build.0 = Release|Any CPU
                {ECEBC9A0-5079-470A-A380-5B80756DEA61}.Debug|Any CPU.ActiveCfg = Debug|Any CPU
                {ECEBC9A0-5079-470A-A380-5B80756DEA61}.Debug|Any CPU.Build.0 = Debug|Any CPU
                {ECEBC9A0-5079-470A-A380-5B80756DEA61}.Release|Any CPU.ActiveCfg = Release|Any CPU
                {ECEBC9A0-5079-470A-A380-5B80756DEA61}.Release|Any CPU.Build.0 = Release|Any CPU
                {8DF06770-ADA4-407D-ABAF-6C222C73962E}.Debug|Any CPU.ActiveCfg = Debug|Any CPU
                {8DF06770-ADA4-407D-ABAF-6C222C73962E}.Debug|Any CPU.Build.0 = Debug|Any CPU
                {8DF06770-ADA4-407D-ABAF-6C222C73962E}.Release|Any CPU.ActiveCfg = Release|Any CPU
                {8DF06770-ADA4-407D-ABAF-6C222C73962E}.Release|Any CPU.Build.0 = Release|Any CPU
        EndGlobalSection
        GlobalSection(SolutionProperties) = preSolution
                HideSolutionNode = FALSE
        EndGlobalSection
        GlobalSection(ExtensibilityGlobals) = postSolution
                SolutionGuid = {089BAFA9-97A5-468A-9FA8-D368A7EE49A6}
        EndGlobalSection
EndGlobal

"""

template_proj_app = r"""
<Project Sdk="Microsoft.NET.Sdk.WindowsDesktop">

  <PropertyGroup>
    <OutputType>WinExe</OutputType>
    <TargetFramework>netcoreapp3.1</TargetFramework>
    <UseWPF>true</UseWPF>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="oelMVCS" Version="1.9.5" />
  </ItemGroup>

  <ItemGroup>
    <ProjectReference Include="..\module\module.csproj" />
    <ProjectReference Include="..\wpf\wpf.csproj" />
  </ItemGroup>

</Project>
"""

template_proj_bridge = r"""
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <TargetFramework>netcoreapp3.1</TargetFramework>
    <AssemblyName>{{org}}.{{mod}}.bridge</AssemblyName>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="oelMVCS" Version="1.9.5" />
  </ItemGroup>

</Project>
"""

template_proj_module = r"""
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <TargetFramework>netcoreapp3.1</TargetFramework>
    <AssemblyName>{{org}}.{{mod}}.module</AssemblyName>
  </PropertyGroup>

  <ItemGroup>
    <ProjectReference Include="..\bridge\bridge.csproj" />
  </ItemGroup>

  <ItemGroup>
    <PackageReference Include="oelMVCS" Version="1.9.5" />
  </ItemGroup>

</Project>
"""

template_proj_wpf = r"""
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <TargetFramework>netcoreapp3.1</TargetFramework>
    <UseWPF>true</UseWPF>
    <AssemblyName>{{org}}.{{mod}}.wpf</AssemblyName>
  </PropertyGroup>

  <ItemGroup>
    <ProjectReference Include="..\bridge\bridge.csproj" />
  </ItemGroup>

  <ItemGroup>
    <PackageReference Include="HandyControl" Version="3.2.0" />
    <PackageReference Include="oelMVCS" Version="1.9.5" />
  </ItemGroup>

</Project>
"""

template_app_AppView_cs = r"""
using System.Collections.Generic;
using XTC.oelMVCS;

namespace app
{
    class AppView : View
    {
        public const string NAME = "AppView";

        protected override void preSetup()
        {
        }

        protected override void setup()
        {
            addRouter("/module/view/attach", this.handleAttachView);
        }

        private void handleAttachView(Model.Status _status, object _data)
        {
            MainWindow mainWindow = App.Current.MainWindow as MainWindow;
            getLogger().Trace("attach view");
            Dictionary<string, object> data = _data as Dictionary<string, object>;
            foreach(string key in data.Keys)
            {
                mainWindow.AddPage(key, data[key]);
            }
        }
    }//class
}//namespace
"""

template_app_AppConfig_cs = r"""
using System.Text.Json;
using XTC.oelMVCS;

namespace app
{
    class ConfigSchema
    {
        public string domain {get;set;}
        public string apikey {get;set;}
    }
    class AppConfig: Config
    {
        public override void Merge(string _content)
        {
            ConfigSchema schema = JsonSerializer.Deserialize<ConfigSchema>(_content);
            fields_["domain"] = Any.FromString(schema.domain);
            fields_["apikey"] = Any.FromString(schema.apikey);
        }
    }//class
}//namespace
"""

template_app_ConsoleLogger_cs = r"""
using System;
using System.Windows.Documents;
using System.Windows.Media;
using XTC.oelMVCS;

namespace app
{
    class ConsoleLogger : Logger
    {
        public System.Windows.Controls.RichTextBox rtbLog { get; set; }
        protected override void trace(string _categoray, string _message)
        {
            this.appendTextColorful(string.Format("TRACE | {0} > {1}", _categoray, _message), Colors.Gray);
        }

        protected override void debug(string _categoray, string _message)
        {
            this.appendTextColorful(string.Format("DEBUG | {0} > {1}", _categoray, _message), Colors.Blue);
        }

        protected override void info(string _categoray, string _message)
        {
            this.appendTextColorful(string.Format("INFO | {0} > {1}", _categoray, _message), Colors.Green);
        }

        protected override void warning(string _categoray, string _message)
        {
            this.appendTextColorful(string.Format("WARN | {0} > {1}", _categoray, _message), Colors.Orange);
        }

        protected override void error(string _categoray, string _message)
        {
            this.appendTextColorful(string.Format("ERROR | {0} > {1}", _categoray, _message), Colors.Red);
        }

        protected override void exception(Exception _exception)
        {
            this.appendTextColorful(string.Format("EXCEPT | > {0}", _exception.ToString()), Colors.Purple);
        }

        private void appendTextColorful(string addtext, Color color)
        {
            var p = new Paragraph();
            var r = new Run(addtext);
            p.Inlines.Add(r);
            p.Foreground = new SolidColorBrush(color);
            rtbLog.Document.Blocks.Add(p);
        }
    }//class
}//namespace

"""

template_app_app_xaml_cs = r"""
using System.Windows;
using System.Text.Json;
using XTC.oelMVCS;
using {{org}}.{{mod}};

namespace app
{
    /// <summary>
    /// Interaction logic for App.xaml
    /// </summary>
    public partial class App : Application
    {
        private Framework framework_ { get; set; }
        private ConsoleLogger logger_ { get; set; }
        private Config config_ { get; set; }

        private void Application_Startup(object sender, StartupEventArgs e)
        {
            // 静态管线注册组件
            registerMVCS();

            ModuleRoot moduleRoot = new ModuleRoot();
            moduleRoot.Inject(framework_);
            moduleRoot.Register();
            ControlRoot controlRoot = new ControlRoot();
            controlRoot.Inject(framework_);
            controlRoot.Register();
            framework_.Setup();
        }

        protected override void OnStartup(StartupEventArgs e)
        {
            logger_ = new ConsoleLogger();
            config_ = new AppConfig();

            string json = JsonSerializer.Serialize(System.Environment.GetEnvironmentVariables());
            config_.Merge(json);

            MainWindow mainWindow = new MainWindow();
            this.MainWindow = mainWindow;
            logger_.rtbLog = mainWindow.rtbLog;
            mainWindow.Show();

            framework_ = new Framework();
            framework_.setLogger(logger_);
            framework_.setConfig(config_);
            framework_.Initialize();

            base.OnStartup(e);


        }

        protected override void OnExit(ExitEventArgs e)
        {
            base.OnExit(e);
            framework_.Release();
            framework_ = null;
        }

        private void registerMVCS()
        {
            BlankModel blankModel = new BlankModel();
            framework_.getStaticPipe().RegisterModel(BlankModel.NAME, blankModel);

            AppView appView = new AppView();
            framework_.getStaticPipe().RegisterView(AppView.NAME, appView);
        }
    }
}

"""

template_app_app_xaml = r"""
<Application x:Class="app.App"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             xmlns:local="clr-namespace:app"
             Startup="Application_Startup" ShutdownMode="OnMainWindowClose">
    <Application.Resources>

    </Application.Resources>
</Application>

"""

template_app_mainwindow_xaml_cs = r"""
using System.Collections.Generic;
using System.Windows;
using System.Windows.Controls;


namespace app
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        public RichTextBox log { get; private set; }

        public static readonly DependencyProperty SubContentProperty = DependencyProperty.Register("SubContent", typeof(object), typeof(MainWindow));
        public object SubContent
        {
            get
            {
                return GetValue(MainWindow.SubContentProperty);
            }
            set
            {
                SetValue(MainWindow.SubContentProperty, value);
            }
        }

        private Dictionary<string, object> pages = new Dictionary<string, object>();

        public MainWindow()
        {
            InitializeComponent();
            log = this.rtbLog;
        }

        public void AddPage(string _key, object _page)
        {
            pages[_key] = _page;
            lbPages.Items.Add(_key);
        }

        private void lbPages_Selected(object sender, RoutedEventArgs e)
        {
            string lbi = lbPages.SelectedItem as string;
            SubContent = pages[lbi];
        }
    }
}

"""

template_app_mainwindow_xaml = r"""
<Window x:Class="app.MainWindow"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        xmlns:d="http://schemas.microsoft.com/expression/blend/2008"
        xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
        xmlns:local="clr-namespace:app"
        mc:Ignorable="d"
        DataContext="{Binding RelativeSource={RelativeSource self}}"
        Title="MainWindow" Height="450" Width="800">

    <DockPanel>
        <ListBox x:Name="lbPages" Margin="12" Width="200" DockPanel.Dock="Left" SelectionChanged="lbPages_Selected">
        </ListBox>
        <RichTextBox Name="rtbLog" Margin="12" Height="120" IsReadOnly="True"  DockPanel.Dock="Bottom"></RichTextBox>
        <UserControl HorizontalAlignment="Stretch" VerticalAlignment="Stretch" Margin="12">
            <ContentPresenter Name="PresenterMain" Content="{Binding SubContent}"/>
        </UserControl>
    </DockPanel>
</Window>
"""


template_app_AssemblyInfo_cs = r"""
using System.Windows;

[assembly: ThemeInfo(
    ResourceDictionaryLocation.None, //where theme specific resource dictionaries are located
                                     //(used if a resource is not found in the page,
                                     // or application resource dictionaries)
    ResourceDictionaryLocation.SourceAssembly //where the generic resource dictionary is located
                                              //(used if a resource is not found in the page,
                                              // app, or any theme specific resource dictionaries)
)]
"""

template_app_blankmodel_cs = r"""
using XTC.oelMVCS;

namespace app
{
    public class BlankModel : Model
    {
        public const string NAME = "BlankModel";
    }
}
"""

template_bridge_view_cs = r"""
using System.Collections.Generic;
using XTC.oelMVCS;
namespace {{org}}.{{mod}}
{
    public interface I{{service}}ViewBridge : View.Facade.Bridge
    {
{{rpc}}
    }
}
"""

template_bridge_extend_view_cs = r"""
namespace {{org}}.{{mod}}
{
    public interface I{{service}}ExtendViewBridge
    {
    }
}
"""


template_bridge_ui_cs = r"""
using System.Collections.Generic;
using XTC.oelMVCS;
namespace {{org}}.{{mod}}
{
    public interface I{{service}}UiBridge : View.Facade.Bridge
    {
        object getRootPanel();
        void Alert(string _message);
        void UpdatePermission(Dictionary<string,string> _permission);
{{rpc}}
    }
}
"""

template_bridge_extend_ui_cs = r"""
namespace {{org}}.{{mod}}
{
    public interface I{{service}}ExtendUiBridge
    {
    }
}
"""

template_module_ModuleRoot_cs = r"""
using System.Collections.Generic;
using XTC.oelMVCS;

namespace {{org}}.{{mod}}
{
    public class ModuleRoot
    {
        public ModuleRoot()
        {
        }

        public void Inject(Framework _framework)
        {
            framework_ = _framework;
        }

        public void Register()
        {
{{register}}
        }

        public void Cancel()
        {
{{cancel}}
        }

        private Framework framework_ = null;
    }
}
"""

template_module_Json_Options_cs = r"""
using System.Text.Encodings.Web;
using System.Text.Json;

namespace {{org}}.{{mod}}
{
    public class JsonOptions
    {
        public static JsonSerializerOptions DefaultSerializerOptions
        {
            get
            {
                var options = new JsonSerializerOptions();
                options.Converters.Add(new AnyProtoConverter());
                options.WriteIndented = true;
                options.Encoder = JavaScriptEncoder.UnsafeRelaxedJsonEscaping;
                return options;
            }
        }

    }
}
"""

template_module_Json_Convert_cs = r"""

using System;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Collections.Generic;
using XTC.oelMVCS;

namespace {{org}}.{{mod}}
{
    /// <summary>
    /// 用于将请求数据序列化为json
    /// </summary>
    class AnyProtoConverter : JsonConverter<Any>
    {
        public override Any Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
        {
            if (reader.TokenType == JsonTokenType.String)
            {
                return Any.FromString(reader.GetString());
            }
            else if (reader.TokenType == JsonTokenType.Number)
            {
                return Any.FromFloat64(reader.GetDouble());
            }
            else if (reader.TokenType == JsonTokenType.True)
            {
                return Any.FromBool(reader.GetBoolean());
            }
            else if (reader.TokenType == JsonTokenType.False)
            {
                return Any.FromBool(reader.GetBoolean());
            }
            else if (reader.TokenType == JsonTokenType.StartArray)
            {
                List<string> ary = new List<string>();
                while (reader.Read())
                {
                    if (reader.TokenType == JsonTokenType.EndArray)
                    {
                        break;
                    }
                    if (reader.TokenType == JsonTokenType.String)
                    {
                        ary.Add(Any.FromString(reader.GetString()).AsString());
                    }
                    else if (reader.TokenType == JsonTokenType.Number)
                    {
                        ary.Add(Any.FromFloat64(reader.GetDouble()).AsString());
                    }
                    else if (reader.TokenType == JsonTokenType.True)
                    {
                        ary.Add(Any.FromBool(reader.GetBoolean()).AsString());
                    }
                    else if (reader.TokenType == JsonTokenType.False)
                    {
                        ary.Add(Any.FromBool(reader.GetBoolean()).AsString());
                    }
                }
                return Any.FromStringAry(ary.ToArray());
            }
            return new Any();
        }

        public override void Write(Utf8JsonWriter writer, Any _value, JsonSerializerOptions options)
        {
            if(_value.IsString())
                writer.WriteStringValue(_value.AsString());
            else if (_value.IsInt32())
                writer.WriteNumberValue(_value.AsInt32());
            else if (_value.IsInt64())
                writer.WriteNumberValue(_value.AsInt64());
            else if (_value.IsFloat32())
                writer.WriteNumberValue(_value.AsFloat32());
            else if (_value.IsFloat64())
                writer.WriteNumberValue(_value.AsFloat64());
            else if (_value.IsBool())
                writer.WriteBooleanValue(_value.AsBool());
            else if (_value.IsBytes())
                writer.WriteStringValue(_value.AsString());
            else if(_value.IsStringAry())
            {
                writer.WriteStartArray();
                foreach(string v in _value.AsStringAry())
                {
                    writer.WriteStringValue(v);
                }
                writer.WriteEndArray();
            }
            else if (_value.IsInt32Ary())
            {
                writer.WriteStartArray();
                foreach (int v in _value.AsInt32Ary())
                {
                    writer.WriteNumberValue(v);
                }
                writer.WriteEndArray();
            }
            else if (_value.IsInt64Ary())
            {
                writer.WriteStartArray();
                foreach (long v in _value.AsInt64Ary())
                {
                    writer.WriteNumberValue(v);
                }
                writer.WriteEndArray();
            }
            else if (_value.IsFloat32Ary())
            {
                writer.WriteStartArray();
                foreach (float v in _value.AsFloat32Ary())
                {
                    writer.WriteNumberValue(v);
                }
                writer.WriteEndArray();
            }
            else if (_value.IsFloat64Ary())
            {
                writer.WriteStartArray();
                foreach (double v in _value.AsFloat64Ary())
                {
                    writer.WriteNumberValue(v);
                }
                writer.WriteEndArray();
            }
            else if (_value.IsBoolAry())
            {
                writer.WriteStartArray();
                foreach (bool v in _value.AsBoolAry())
                {
                    writer.WriteBooleanValue(v);
                }
                writer.WriteEndArray();
            }
            else if (_value.IsStringMap())
            {
                writer.WriteStartObject();
                foreach (var pair in _value.AsStringMap())
                {
                    writer.WriteString(pair.Key, pair.Value);
                }
                writer.WriteEndObject();
            }
            else if (_value.IsInt32Map())
            {
                writer.WriteStartObject();
                foreach (var pair in _value.AsInt32Map())
                {
                    writer.WriteNumber(pair.Key, pair.Value);
                }
                writer.WriteEndObject();
            }
            else if (_value.IsInt64Map())
            {
                writer.WriteStartObject();
                foreach (var pair in _value.AsInt64Map())
                {
                    writer.WriteNumber(pair.Key, pair.Value);
                }
                writer.WriteEndObject();
            }
            else if (_value.IsFloat32Map())
            {
                writer.WriteStartObject();
                foreach (var pair in _value.AsFloat32Map())
                {
                    writer.WriteNumber(pair.Key, pair.Value);
                }
                writer.WriteEndObject();
            }
            else if (_value.IsFloat64Map())
            {
                writer.WriteStartObject();
                foreach (var pair in _value.AsFloat64Map())
                {
                    writer.WriteNumber(pair.Key, pair.Value);
                }
                writer.WriteEndObject();
            }
            else if (_value.IsBoolMap())
            {
                writer.WriteStartObject();
                foreach (var pair in _value.AsBoolMap())
                {
                    writer.WriteBoolean(pair.Key, pair.Value);
                }
                writer.WriteEndObject();
            }
        }
    }//class

}//namespace
"""

template_module_Model_cs = r"""
using System;
using XTC.oelMVCS;

namespace {{org}}.{{mod}}
{
    public class {{service}}Model : {{service}}BaseModel
    {
        public class {{service}}Status : {{service}}BaseStatus
        {
        }
        public const string NAME = "{{org}}.{{mod}}.{{service}}Model";


    }
}
"""

template_module_BaseModel_cs = r"""
using System;
using XTC.oelMVCS;

namespace {{org}}.{{mod}}
{
    public class {{service}}BaseModel : Model
    {

        public class {{service}}BaseStatus : Model.Status
        {
            public const string NAME = "{{org}}.{{mod}}.{{service}}Status";
        }

        protected {{service}}Controller controller {get;set;}

        protected override void preSetup()
        {
            controller = findController({{service}}Controller.NAME) as {{service}}Controller;
            Error err;
            status_ = spawnStatus<{{service}}Model.{{service}}Status>({{service}}Model.{{service}}Status.NAME, out err);
            if(0 != err.getCode())
            {
                getLogger().Error(err.getMessage());
            }
            else
            {
                getLogger().Trace("setup {{org}}.{{mod}}.{{service}}Status");
            }
        }

        protected override void setup()
        {
            getLogger().Trace("setup {{org}}.{{mod}}.{{service}}Model");
        }

        protected override void preDismantle()
        {
            Error err;
            killStatus({{service}}Model.{{service}}Status.NAME, out err);
            if(0 != err.getCode())
            {
                getLogger().Error(err.getMessage());
            }
        }

        protected {{service}}Model.{{service}}Status status
        {
            get
            {
                return status_ as {{service}}Model.{{service}}Status;
            }
        }

{{rpc}}

    }
}
"""

template_module_View_cs = r"""
using System.Collections.Generic;
using XTC.oelMVCS;

namespace {{org}}.{{mod}}
{
    public class {{service}}View: {{service}}BaseView
    {
        public const string NAME = "{{org}}.{{mod}}.{{service}}View";
    }
}
"""


template_module_BaseView_cs = r"""
using System.Text.Json;
using System.Collections.Generic;
using XTC.oelMVCS;

namespace {{org}}.{{mod}}
{
    public class {{service}}BaseView: View
    {
        protected Facade facade = null;
        protected {{service}}Model model = null;
        protected I{{service}}UiBridge bridge = null;

        protected override void preSetup()
        {
            model = findModel({{service}}Model.NAME) as {{service}}Model;
            var service = findService({{service}}Service.NAME) as {{service}}Service;
            facade = findFacade("{{org}}.{{mod}}.{{service}}Facade");
            {{service}}ViewBridge vb = new {{service}}ViewBridge();
            vb.view = this as {{service}}View;
            vb.service = service;
            facade.setViewBridge(vb);
        }

        protected override void setup()
        {
            getLogger().Trace("setup {{org}}.{{mod}}.{{service}}View");
{{routers}}
        }

        protected override void postSetup()
        {
            bridge = facade.getUiBridge() as I{{service}}UiBridge;
            object rootPanel = bridge.getRootPanel();
            // 通知主程序挂载界面
            Dictionary<string, object> data = new Dictionary<string, object>();
            data["{{org}}.{{mod}}.{{service}}"] = rootPanel;
            model.Broadcast("/module/view/attach", data);
            // 监听权限更新
            addRouter("/permission/updated", this.handlePermissionUpdated);
        }

        protected void handlePermissionUpdated(Model.Status _status, object _data)
        {
            Dictionary<string, string> permission = (Dictionary<string,string>) _data;
            bridge.UpdatePermission(permission);
        }


        public void Alert(string _message)
        {
            bridge.Alert(_message);
        }
{{handlers}}
    }
}
"""

template_module_Controller_cs = r"""
using System;
using XTC.oelMVCS;

namespace {{org}}.{{mod}}
{
    public class {{service}}Controller: {{service}}BaseController
    {
        public const string NAME = "{{org}}.{{mod}}.{{service}}Controller";
    }
}
"""

template_module_BaseController_cs = r"""
using System;
using XTC.oelMVCS;

namespace {{org}}.{{mod}}
{
    public class {{service}}BaseController: Controller
    {

        protected {{service}}View view {get;set;}

        protected override void preSetup()
        {
            view = findView({{service}}View.NAME) as {{service}}View;
        }

        protected override void setup()
        {
            getLogger().Trace("setup {{org}}.{{mod}}.{{service}}Controller");
        }
    }
}
"""

template_module_BaseViewBridge_cs = r"""
using System.Collections.Generic;
using System.Text.Json;
using XTC.oelMVCS;

namespace {{org}}.{{mod}}
{
    public class {{service}}BaseViewBridge : I{{service}}ViewBridge
    {
        public {{service}}View view{ get; set; }
        public {{service}}Service service{ get; set; }

{{rpc}}

    }
}
"""

template_module_ViewBridge_cs = r"""
using System.Collections.Generic;
using System.Text.Json;
using XTC.oelMVCS;

namespace {{org}}.{{mod}}
{
    public class {{service}}ViewBridge : {{service}}BaseViewBridge, I{{service}}ExtendViewBridge
    {
    }
}
"""

template_module_Service_cs = r"""
using System.IO;
using System.Net;
using System.Text.Json;
using System.Collections.Generic;
using XTC.oelMVCS;

namespace {{org}}.{{mod}}
{
    public class {{service}}Service: {{service}}BaseService
    {
        public const string NAME = "{{org}}.{{mod}}.{{service}}Service";
    }
}
"""


template_module_BaseService_cs = r"""
using System.IO;
using System.Net;
using System.Text.Json;
using System.Collections.Generic;
using XTC.oelMVCS;

namespace {{org}}.{{mod}}
{
    public class {{service}}BaseService: Service
    {
        protected {{service}}Model model = null;
        protected Options options = null;

        protected override void preSetup()
        {
            options = new Options();
            options.header["apikey"] = getConfig().getField("apikey").AsString();
            model = findModel({{service}}Model.NAME) as {{service}}Model;
        }

        protected override void setup()
        {
            getLogger().Trace("setup {{org}}.{{mod}}.{{service}}Service");
        }
{{rpc}}

        protected override void asyncRequest(string _url, string _method, Dictionary<string, Any> _params, OnReplyCallback _onReply, OnErrorCallback _onError, Options _options)
        {
            doAsyncRequest(_url, _method, _params, _onReply, _onError, _options);
        }

        protected async void doAsyncRequest(string _url, string _method, Dictionary<string, Any> _params, OnReplyCallback _onReply, OnErrorCallback _onError, Options _options)
        {
            string reply = "";
            try
            {
                HttpWebRequest req = (HttpWebRequest)WebRequest.Create(_url);
                req.Method = _method;
                req.ContentType = "application/json;charset=utf-8";
                foreach (var pair in options.header)
                    req.Headers.Add(pair.Key, pair.Value);
                byte[] data = System.Text.Json.JsonSerializer.SerializeToUtf8Bytes(_params, JsonOptions.DefaultSerializerOptions);
                req.ContentLength = data.Length;
                using (Stream reqStream = req.GetRequestStream())
                {
                    reqStream.Write(data, 0, data.Length);
                }
                HttpWebResponse rsp = await req.GetResponseAsync() as HttpWebResponse;
                if (rsp == null)
                {
                    _onError(Error.NewNullErr("HttpWebResponse is null"));
                    return;
                }
                if (rsp.StatusCode != HttpStatusCode.OK)
                {
                    rsp.Close();
                    _onError(new Error(rsp.StatusCode.GetHashCode(), "HttpStatusCode != 200"));
                    return;
                }
                StreamReader sr;
                using (sr = new StreamReader(rsp.GetResponseStream()))
                {
                    reply = sr.ReadToEnd();
                }
                sr.Close();
            }
            catch (System.Exception ex)
            {
                _onError(Error.NewException(ex));
                return;
            }
            _onReply(reply);
        }
    }
}
"""


template_module_Protocol_cs = r"""
using System;
using System.Text;
using System.Text.Json.Serialization;
using System.Collections.Generic;
using XTC.oelMVCS;

namespace {{org}}.{{mod}}.Proto
{
{{proto}}
}
"""

template_wpf_BaseControlRoot_cs = r"""
using XTC.oelMVCS;

namespace wpf
{
}

namespace {{org}}.{{mod}}
{
    public class BaseControlRoot
    {
{{members}}
        public void Inject(Framework _framework)
        {
            framework_ = _framework;
        }

        protected void register()
        {
{{register}}
        }

        protected void cancel()
        {
{{cancel}}
        }

        protected Framework framework_ = null;
    }
}
"""

template_wpf_Reply_cs = r"""
namespace {{org}}.{{mod}}
{
    public class Reply
    {
        public class Status
        {
            public int code { get; set; }
            public string message { get; set; }
        }

        public Status status { get; set; }

        public Reply()
        {
            status = new Status();
        }
    }
}
"""

template_wpf_ControlRoot_cs = r"""
using XTC.oelMVCS;

namespace {{org}}.{{mod}}
{
    public class ControlRoot : BaseControlRoot
    {
        public ControlRoot()
        {
        }

        public void Register()
        {
            register();
        }

        public void Cancel()
        {
            cancel();
        }
    }
}
"""

template_wpf_BaseUiBridge_cs = r"""
using System.Text.Json;
using System.Collections.Generic;
using HandyControl.Controls;

namespace {{org}}.{{mod}}
{
    public class Base{{service}}UiBridge: I{{service}}UiBridge
    {
        public {{service}}Control control {get;set;}

        public object getRootPanel()
        {
            return control;
        }

        public virtual void Alert(string _message) {}

        public virtual void UpdatePermission(Dictionary<string, string> _permission) {}


{{rpc}}

    }
}
"""

template_wpf_Facade_cs = r"""
using XTC.oelMVCS;

namespace {{org}}.{{mod}}
{
    public class {{service}}Facade : View.Facade
    {
        public const string NAME = "{{org}}.{{mod}}.{{service}}Facade";
    }
}
"""

template_wpf_Control_cs = r"""
using System.Windows.Controls;
using System.Collections.Generic;

namespace {{org}}.{{mod}}
{
    public partial class {{service}}Control: UserControl
    {
        public class {{service}}UiBridge : Base{{service}}UiBridge, I{{service}}ExtendUiBridge
        {
        }

        public {{service}}Facade facade { get; set; }

        public {{service}}Control()
        {
            InitializeComponent();
        }
    }
}
"""

template_wpf_Control_xaml = r"""
<UserControl x:Class="{{org}}.{{mod}}.{{service}}Control"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
             xmlns:d="http://schemas.microsoft.com/expression/blend/2008"
             xmlns:local="clr-namespace:{{org}}.{{mod}}"
             mc:Ignorable="d"
             d:DesignHeight="450" d:DesignWidth="800">
    <StackPanel Background="Black">
    </StackPanel>
</UserControl>
"""

template_module_register_block = r"""
                // 注册数据层
                framework_.getStaticPipe().RegisterModel({{service}}Model.NAME, new {{service}}Model());
                // 注册视图层
                framework_.getStaticPipe().RegisterView({{service}}View.NAME, new {{service}}View());
                // 注册控制层
                framework_.getStaticPipe().RegisterController({{service}}Controller.NAME, new {{service}}Controller());
                // 注册服务层
                framework_.getStaticPipe().RegisterService({{service}}Service.NAME, new {{service}}Service());
"""

template_module_cancel_block = r"""
                // 注销服务层
                framework_.getStaticPipe().CancelService({{service}}Service.NAME);
                // 注销控制层
                framework_.getStaticPipe().CancelController({{service}}Controller.NAME);
                // 注销视图层
                framework_.getStaticPipe().CancelView({{service}}View.NAME);
                // 注销数据层
                framework_.getStaticPipe().CancelModel({{service}}Model.NAME);
"""

template_module_model_method = r"""
        public virtual void Save{{rpc}}(Proto.{{rsp}} _rsp) 
        {
             this.Bubble("_.reply.arrived:{{org}}/{{mod}}/{{service}}/{{rpc}}", _rsp);
        }
"""

template_view_router = r"""
            addObserver({{service}}Model.NAME, "_.reply.arrived:{{org}}/{{mod}}/{{service}}/{{rpc}}", this.handleReceive{{service}}{{rpc}});
"""

template_view_handler = r"""
        private void handleReceive{{service}}{{rpc}}(Model.Status _status, object _data)
        {
            var rsp = _data as Proto.{{rsp}};
            if(null == rsp)
            {
                getLogger().Error("rsp of {{service}}/{{rpc}} is null");
                return;
            }
            string json = JsonSerializer.Serialize(rsp, JsonOptions.DefaultSerializerOptions);
            bridge.Receive{{rpc}}(json);
        }
"""

template_viewbridge_method = r"""
            public void On{{rpc}}Submit(string _json)
            {
                var req = JsonSerializer.Deserialize<Proto.{{req}}>(_json, JsonOptions.DefaultSerializerOptions);
                service.Post{{rpc}}(req);
            }
"""

template_service_method = r"""
            public void Post{{rpc}}(Proto.{{req}} _request)
            {
                Dictionary<string, Any> paramMap = new Dictionary<string, Any>();
    {{assign}}
                post(string.Format("{0}/{{org}}/{{mod}}/{{service}}/{{rpc}}", getConfig().getField("domain").AsString()), paramMap, (_reply) =>
                {
                    var rsp = JsonSerializer.Deserialize<Proto.{{rsp}}>(_reply, JsonOptions.DefaultSerializerOptions);
                    model.Save{{rpc}}(rsp);
                }, (_err) =>
                {
                    getLogger().Error(_err.getMessage());
                }, null);
            }
"""

template_proto_class = r"""
            public class {{message}}
            {
                public {{message}}()
                {
    {{assign}}
                }
    {{field}}
            }
"""

template_wpf_members_block = r"""
        protected {{service}}Facade facade{{service}}_ {get;set;}
        protected {{service}}Control control{{service}}_ {get;set;}
        protected {{service}}Control.{{service}}UiBridge ui{{service}}Bridge_  {get;set;}
"""

template_wpf_register_block = r"""
                // 注册UI装饰
                facade{{service}}_ = new {{service}}Facade();
                framework_.getStaticPipe().RegisterFacade({{service}}Facade.NAME, facade{{service}}_);
                control{{service}}_ = new {{service}}Control();
                control{{service}}_.facade = facade{{service}}_;
                ui{{service}}Bridge_ = new {{service}}Control.{{service}}UiBridge();
                ui{{service}}Bridge_.control = control{{service}}_;
                facade{{service}}_.setUiBridge(ui{{service}}Bridge_);
"""

template_wpf_cancel_block = r"""
                // 注销UI装饰
                framework_.getStaticPipe().CancelFacade({{service}}Facade.NAME);
"""
template_wpf_receive_block = r"""
        public virtual void Receive{{rpc}}(string _json) 
        {
            Reply reply = JsonSerializer.Deserialize<Reply>(_json);
            if (reply.status.code == 0)
                Growl.Success("Success", "StatusGrowl");
            else
                Growl.Warning(reply.status.message, "StatusGrowl");
        }
"""
