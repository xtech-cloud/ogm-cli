import os
import sys
import re
import yaml
from typing import Dict, List, Tuple

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
    <PackageReference Include="oelMVCS" Version="1.9.4" />
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
    <PackageReference Include="oelMVCS" Version="1.9.4" />
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
    <PackageReference Include="oelMVCS" Version="1.9.4" />
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
    <PackageReference Include="oelMVCS" Version="1.9.4" />
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
    }
    class AppConfig: Config
    {
        public override void Merge(string _content)
        {
            ConfigSchema schema = JsonSerializer.Deserialize<ConfigSchema>(_content);
            fields_["domain"] = Any.FromString(schema.domain);
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

templete_bridge_view_cs = r"""
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

templete_bridge_ui_cs = r"""
using System.Collections.Generic;
using XTC.oelMVCS;
namespace {{org}}.{{mod}}
{
    public interface I{{service}}UiBridge : View.Facade.Bridge
    {
        object getRootPanel();
        void Alert(string _message);
        void UpdatePermission(Dictionary<string,string> _permission);
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

{{rpc}}

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
    }
}
"""

template_module_View_cs = r"""
using System;
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
using System;
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

template_module_ViewBridge_cs = r"""
using System.Collections.Generic;
using System.Text.Json;
using XTC.oelMVCS;

namespace {{org}}.{{mod}}
{
    public class {{service}}ViewBridge : I{{service}}ViewBridge
    {
        public {{service}}View view{ get; set; }
        public {{service}}Service service{ get; set; }

{{rpc}}

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

        protected override void preSetup()
        {
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
                req.ContentType =
                "application/json;charset=utf-8";
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

template_wpf_ControlRoot_cs = r"""
using XTC.oelMVCS;

namespace wpf
{
}

namespace {{org}}.{{mod}}
{
    public class ControlRoot
    {
        public ControlRoot()
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
        public class {{service}}UiBridge : I{{service}}UiBridge
        {
            public {{service}}Control control { get; set; }

            public object getRootPanel()
            {
                return control;
            }

            public void Alert(string _message)
            {
            }

            public void UpdatePermission(Dictionary<string,string> _permission)
            {
            }
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

##############################################################################
##############################################################################
##############################################################################

org_name = ""
mod_name = ""

if '' == org_name:
    print('org is empty')
    sys.exit(0)

if '' == mod_name:
    print('mod is empty')
    sys.exit(0)

proto_dir = "./"


services: Dict[str, Dict[str, Tuple]] = {}
"""
service Healthy {
  rpc Echo(EchoRequest) returns (EchoResponse) {}
}
转换格式为
{
    startkit:
    {
        healthy: (EchoRequest, EchoResponse)
    }
}
"""

messages: Dict[str, List[Tuple]] = {}
"""
message EchoRequest {
  string msg = 1;  // 消息
}
转换为
{
    EchoRequest:
    [
        (msg, string, 消息),
    ]
}
"""

enums: List[str] = []

# protobuf 到 C# 类型的转换
type_dict = {
        "string": "string",
        "int32": "int",
        "uint32": "uint",
        "int64": "long",
        "uint64": "ulong",
        "bool": "bool",
        "float32": "float",
        "float64": "double",
        "bytes": "byte[]",
        "enum": "int",
        }

# C# 类型到Any的转换
type_to_any = {
        "string": "string",
        "int": "int32",
        "uint": "int32",
        "long": "int64",
        "ulong": "int64",
        "bool": "bool",
        "float": "float32",
        "double": "float64",
        "byte[]": "bytes",
        }

type_default_value = {
        "string": "\"\"",
        "int32": "0",
        "uint32": "0",
        "int64": "0",
        "uint64": "0",
        "bool": "false",
        "float32": "0",
        "float64": "0",
        "bytes": "new byte[0]",
        "enum": "0",
        }

# 解析协议文件
for entry in os.listdir(proto_dir):
    # 跳过不是.proto的文件
    if not entry.endswith(".proto"):
        continue
    # 跳过healthy.proto
    if entry == "healthy.proto":
        continue
    proto_name = os.path.splitext(entry)[0]
    with open(os.path.join(proto_dir, entry), "r", encoding="utf-8") as rf:
        content = rf.read()
        rf.close()
        #############################
        # 提取enum名
        #############################
        match = re.findall(r".*?enum\s*(.*?)\s*\{", content, re.S)
        for enum_name in match:
            enums.append(enum_name)
        #############################
        # 提取service语句块
        #############################
        match = re.findall(r".*?service\s*(.*?\}\s*\})", content, re.S)
        for service_block in match:
            # 提取服务名
            match = re.findall(r"(\w*?)\s*\{", service_block, re.S)
            service_name = match[0]
            services[service_name] = {}
            # 提取服务方法
            for line in str.splitlines(service_block):
                # 跳过不包含rpc的行
                if str.find(line, "rpc") < 0:
                    continue
                # 跳过包含stream的行
                if str.find(line, "stream") >= 0:
                    continue
                # 提取rpc语句块
                match = re.findall(r".*rpc\s*(.*?)\s*\{\s*\}", line, re.S)
                if len(match) == 0:
                    continue
                rpc_block = match[0]
                # 提取方法名
                match = re.findall(r"^(.*?)\s*\(", rpc_block, re.S)
                if len(match) == 0:
                    continue
                rpc_name = match[0]
                # 提取请求
                match = re.findall(r"\(\s*(.*?)\s*\)\s*returns", rpc_block, re.S)
                req_name = ""
                if len(match) > 0:
                    req_name = match[0]
                # 提取回复
                match = re.findall(r"returns\s*\(\s*(.*?)\s*\)", rpc_block, re.S)
                rsp_name = ""
                if len(match) > 0:
                    rsp_name = match[0]
                services[service_name][rpc_name] = (req_name, rsp_name)
        #############################
        # 提取message语句块
        #############################
        match = re.findall(r".*?message\s*(.*?\})", content, re.S)
        for message_block in match:
            # 提取消息名
            match = re.findall(r"(\w*?)\s*\{", message_block, re.S)
            message_name = match[0]
            messages[message_name] = []
            # 提取字段
            for line in str.splitlines(message_block):
                # 跳过不包含=的行
                if str.find(line, "=") < 0:
                    continue
                # 跳过不包含;的行
                if str.find(line, ";") < 0:
                    continue
                isRepeated = False
                if line.find("repeated") >= 0:
                    isRepeated = True
                    line = line.replace("repeated", "")
                # 提取字段类型
                match = re.findall(r"\s*(.*)\s+\w+\s+=", line, re.S)
                field_type = ""
                if len(match) > 0:
                    field_type = match[0]
                if isRepeated:
                    field_type = field_type + "[]"
                if field_type.startswith('map'):
                    #field_type = 'System.Collections.Generic.Dictionary' + field_type[3:]
                    match = re.findall(r",\s+(\w*?)\>", field_type, re.S)
                    field_type = match[0]+ "<>"
                # 提取字段名
                match = re.findall(r"\s+(\w+)\s+=", line, re.S)
                field_name = ""
                if len(match) > 0:
                    field_name = match[0]
                # 提取字段注释
                match = re.findall(r"//\s+(\w+)", line, re.S)
                field_remark = ""
                if len(match) > 0:
                    field_remark = str.strip(match[0])
                messages[message_name].append((field_name, field_type, field_remark))


# 生成..gitignore文件
os.makedirs("vs2019", exist_ok=True)
with open("./vs2019/.gitignore", "w", encoding="utf-8") as wf:
    wf.write(template_gitignore)
    wf.close()

# 生成.sln文件
os.makedirs("vs2019", exist_ok=True)
with open("./vs2019/{}-{}.sln".format(org_name, mod_name), "w", encoding="utf-8") as wf:
    wf.write(template_sln)
    wf.close()

# -----------------------------------------------------------------------------
# 生成 app 解决方案
# -----------------------------------------------------------------------------
os.makedirs("vs2019/app", exist_ok=True)
# 生成.proj文件
with open("./vs2019/app/app.csproj", "w", encoding="utf-8") as wf:
    wf.write(template_proj_app)
    wf.close()

# 生成App.xaml
with open("./vs2019/app/App.xaml", "w", encoding="utf-8") as wf:
    wf.write(template_app_app_xaml)
    wf.close()

# 生成App.xaml.cs
with open("./vs2019/app/App.xaml.cs", "w", encoding="utf-8") as wf:
    code = template_app_app_xaml_cs
    code = code.replace("{{org}}", org_name)
    code = code.replace("{{mod}}", mod_name)
    wf.write(code)
    wf.close()

# 生成AppConfig.cs
with open("./vs2019/app/AppConfig.cs", "w", encoding="utf-8") as wf:
    wf.write(template_app_AppConfig_cs)
    wf.close()

# 生成AppView.cs
with open("./vs2019/app/AppView.cs", "w", encoding="utf-8") as wf:
    wf.write(template_app_AppView_cs)
    wf.close()

# 生成AssemblyInfo.cs
with open("./vs2019/app/AssemblyInfo", "w", encoding="utf-8") as wf:
    wf.write(template_app_AssemblyInfo_cs)
    wf.close()

# 生成BlankModel.cs
with open("./vs2019/app/BlankModel.cs", "w", encoding="utf-8") as wf:
    wf.write(template_app_blankmodel_cs)
    wf.close()

# 生成ConsoleLogger.cs
with open("./vs2019/app/ConsoleLogger.cs", "w", encoding="utf-8") as wf:
    wf.write(template_app_ConsoleLogger_cs)
    wf.close()

# 生成MainWindow.xaml
with open("./vs2019/app/MainWindow.xaml", "w", encoding="utf-8") as wf:
    wf.write(template_app_mainwindow_xaml)
    wf.close()

# 生成MainWindow.xaml.cs
with open("./vs2019/app/MainWindow.xaml.cs", "w", encoding="utf-8") as wf:
    wf.write(template_app_mainwindow_xaml_cs)
    wf.close()

# -----------------------------------------------------------------------------
# 生成 bridge 解决方案
# -----------------------------------------------------------------------------
os.makedirs("vs2019/bridge", exist_ok=True)
# 生成.proj文件
with open("./vs2019/bridge/bridge.csproj", "w", encoding="utf-8") as wf:
    wf.write(
            template_proj_bridge.replace("{{org}}", org_name).replace("{{mod}}", mod_name)
            )
    wf.close()

# 生成ViewBridge.cs文件
for service in services.keys():
    with open(
            "./vs2019/bridge/I{}ViewBridge.cs".format(service), "w", encoding="utf-8"
            ) as wf:
        template_method = r"        void On{{rpc}}Submit(string _json);"
        rpc_block = ""
        for rpc_name in services[service].keys():
            rpc = template_method.replace("{{rpc}}", rpc_name)
            rpc_block = rpc_block + str.format("{}\n", rpc)
        code = templete_bridge_view_cs
        code = code.replace("{{org}}", org_name)
        code = code.replace("{{mod}}", mod_name)
        code = code.replace("{{service}}", service)
        code = code.replace("{{rpc}}", rpc_block)
        wf.write(code)
        wf.close()

# 生成UiBridge.cs文件
for service in services.keys():
    with open(
            "./vs2019/bridge/I{}UiBridge.cs".format(service), "w", encoding="utf-8"
            ) as wf:
        code = templete_bridge_ui_cs
        code = code.replace("{{org}}", org_name)
        code = code.replace("{{mod}}", mod_name)
        code = code.replace("{{service}}", service)
        wf.write(code)
        wf.close()


# -----------------------------------------------------------------------------
# 生成 module 解决方案
# -----------------------------------------------------------------------------
os.makedirs("vs2019/module", exist_ok=True)
# 生成.proj文件
with open("./vs2019/module/module.csproj", "w", encoding="utf-8") as wf:
    wf.write(
            template_proj_module.replace("{{org}}", org_name).replace("{{mod}}", mod_name)
            )
    wf.close()


# 生成ModuleRoot.cs文件
with open("./vs2019/module/ModuleRoot.cs", "w", encoding="utf-8") as wf:
    template_register_block = r"""
            // 注册数据层
            framework_.getStaticPipe().RegisterModel({{service}}Model.NAME, new {{service}}Model());
            // 注册视图层
            framework_.getStaticPipe().RegisterView({{service}}View.NAME, new {{service}}View());
            // 注册控制层
            framework_.getStaticPipe().RegisterController({{service}}Controller.NAME, new {{service}}Controller());
            // 注册服务层
            framework_.getStaticPipe().RegisterService({{service}}Service.NAME, new {{service}}Service());
    """
    template_cancel_block = r"""
            // 注销服务层
            framework_.getStaticPipe().CancelService({{service}}Service.NAME);
            // 注销控制层
            framework_.getStaticPipe().CancelController({{service}}Controller.NAME);
            // 注销视图层
            framework_.getStaticPipe().CancelView({{service}}View.NAME);
            // 注销数据层
            framework_.getStaticPipe().CancelModel({{service}}Model.NAME);
    """
    register_block = ""
    cancel_block = ""
    for service in services.keys():
        register_block = register_block + template_register_block.replace(
                "{{service}}", service
                )
        cancel_block = cancel_block + template_cancel_block.replace(
                "{{service}}", service
                )
    code = template_module_ModuleRoot_cs
    code = code.replace("{{org}}", org_name)
    code = code.replace("{{mod}}", mod_name)
    code = code.replace("{{register}}", register_block)
    code = code.replace("{{cancel}}", cancel_block)
    wf.write(code)
    wf.close()

# 生成Model.cs文件
for service in services.keys():
    with open(
            "./vs2019/module/{}Model.cs".format(service), "w", encoding="utf-8"
            ) as wf:
        template_method = r"        public void Save{{rpc}}(Proto.{{rsp}} _rsp) { }"
        rpc_block = ""
        for rpc_name in services[service].keys():
            rpc = template_method.replace("{{rpc}}", rpc_name)
            rpc = rpc.replace("{{rsp}}", services[service][rpc_name][1])
            rpc_block = rpc_block + str.format("{}\n", rpc)
        code = template_module_Model_cs
        code = code.replace("{{org}}", org_name)
        code = code.replace("{{mod}}", mod_name)
        code = code.replace("{{service}}", service)
        code = code.replace("{{rpc}}", rpc_block)
        wf.write(code)
        wf.close()

# 生成BaseModel.cs文件
for service in services.keys():
    with open(
            "./vs2019/module/{}BaseModel.cs".format(service), "w", encoding="utf-8"
            ) as wf:
        code = template_module_BaseModel_cs
        code = code.replace("{{org}}", org_name)
        code = code.replace("{{mod}}", mod_name)
        code = code.replace("{{service}}", service)
        wf.write(code)
        wf.close()

# 生成View.cs文件
for service in services.keys():
    with open(
            "./vs2019/module/{}View.cs".format(service), "w", encoding="utf-8"
            ) as wf:
        code = template_module_View_cs
        code = code.replace("{{org}}", org_name)
        code = code.replace("{{mod}}", mod_name)
        code = code.replace("{{service}}", service)
        wf.write(code)
        wf.close()

# 生成BaseView.cs文件
for service in services.keys():
    template_router = r"""
           addRouter("/{{org}}/{{mod}}/{{service}}/{{rpc}}", this.handle{{service}}{{rpc}});
    """
    template_handler = r"""
        private void handle{{service}}{{rpc}}(Model.Status _status, object _data)
        {
            var rsp = (Proto.{{rsp}})_data;
            if(rsp._status._code.AsInt32() == 0)
                bridge.Alert("Success");
            else
                bridge.Alert(string.Format("Failure：\n\nCode: {0}\nMessage:\n{1}", rsp._status._code.AsInt32(), rsp._status._message.AsString()));
        }
    """
    with open("./vs2019/module/{}BaseView.cs".format(service), "w", encoding="utf-8") as wf:
        router_block = ''
        handler_block = ''
        for rpc_name in services[service].keys():
            rsp_name = services[service][rpc_name][1]
            router_block = router_block + template_router.replace("{{org}}", org_name).replace("{{mod}}", mod_name).replace("{{service}}", service).replace("{{rpc}}", rpc_name)
            handler_block = handler_block + template_handler.replace("{{service}}", service).replace("{{rpc}}", rpc_name).replace("{{rsp}}", rsp_name)

        code = template_module_BaseView_cs
        code = code.replace("{{org}}", org_name)
        code = code.replace("{{mod}}", mod_name)
        code = code.replace("{{service}}", service)
        code = code.replace("{{routers}}", router_block)
        code = code.replace("{{handlers}}", handler_block)
        wf.write(code)
        wf.close()

# 生成Controller.cs文件
for service in services.keys():
    with open(
            "./vs2019/module/{}Controller.cs".format(service), "w", encoding="utf-8"
            ) as wf:
        code = template_module_Controller_cs
        code = code.replace("{{org}}", org_name)
        code = code.replace("{{mod}}", mod_name)
        code = code.replace("{{service}}", service)
        wf.write(code)
        wf.close()

# 生成BaseController.cs文件
for service in services.keys():
    with open(
            "./vs2019/module/{}BaseController.cs".format(service), "w", encoding="utf-8"
            ) as wf:
        code = template_module_BaseController_cs
        code = code.replace("{{org}}", org_name)
        code = code.replace("{{mod}}", mod_name)
        code = code.replace("{{service}}", service)
        wf.write(code)
        wf.close()

# 生成ViewBridge.cs文件
for service in services.keys():
    with open(
            "./vs2019/module/{}ViewBridge.cs".format(service), "w", encoding="utf-8"
            ) as wf:
        template_method = r"""
        public void On{{rpc}}Submit(string _json)
        {
            var options = new JsonSerializerOptions();
            options.Converters.Add(new AnyProtoConverter());
            var req = JsonSerializer.Deserialize<Proto.{{req}}>(_json, options);
            service.Post{{rpc}}(req);
        }
        """
        rpc_block = ""
        for rpc_name in services[service].keys():
            req_name = services[service][rpc_name][0]
            rpc = template_method.replace("{{rpc}}", rpc_name)
            rpc = rpc.replace("{{req}}", req_name)
            rpc_block = rpc_block + str.format("{}\n", rpc)
        code = template_module_ViewBridge_cs
        code = code.replace("{{org}}", org_name)
        code = code.replace("{{mod}}", mod_name)
        code = code.replace("{{service}}", service)
        code = code.replace("{{rpc}}", rpc_block)
        wf.write(code)
        wf.close()


# 生成Service.cs文件
for service in services.keys():
    with open(
            "./vs2019/module/{}Service.cs".format(service), "w", encoding="utf-8"
            ) as wf:
        code = template_module_Service_cs
        code = code.replace("{{org}}", org_name)
        code = code.replace("{{mod}}", mod_name)
        code = code.replace("{{service}}", service)
        wf.write(code)
        wf.close()

# 生成BaseService.cs文件
for service in services.keys():
    with open(
            "./vs2019/module/{}BaseService.cs".format(service), "w", encoding="utf-8"
            ) as wf:
        template_method = r"""
        public void Post{{rpc}}(Proto.{{req}} _request)
        {
            Dictionary<string, Any> paramMap = new Dictionary<string, Any>();
{{assign}}
            post(string.Format("{0}/{{org}}/{{mod}}/{{service}}/{{rpc}}", getConfig().getField("domain").AsString()), paramMap, (_reply) =>
            {
                var options = new JsonSerializerOptions();
                options.Converters.Add(new AnyProtoConverter());
                var rsp = JsonSerializer.Deserialize<Proto.{{rsp}}>(_reply, options);
                model.Save{{rpc}}(rsp);
            }, (_err) =>
            {
                getLogger().Error(_err.getMessage());
            }, null);
        }
        """
        rpc_block = ""
        for rpc_name in services[service].keys():
            rpc = template_method.replace("{{org}}", org_name)
            rpc = rpc.replace("{{mod}}", mod_name)
            rpc = rpc.replace("{{service}}", service)
            rpc = rpc.replace("{{rpc}}", rpc_name)
            rpc = rpc.replace("{{req}}", services[service][rpc_name][0])
            rpc = rpc.replace("{{rsp}}", services[service][rpc_name][1])
            rpc_block = rpc_block + str.format("{}\n", rpc)
            req_name = services[service][rpc_name][0]
            assign_block = ""
            for field in messages[req_name]:
                field_name = field[0]
                field_type = field[1]
                # 转换枚举类型
                if field_type in enums:
                    field_type = "enum"
                # 转换类型
                if field_type in type_dict.keys():
                    field_type = type_dict[field_type]

                if field_type in type_dict.values() or field_type.endswith('[]') or field_type.endswith('{}'):
                    assign_block = assign_block + str.format(
                        '            paramMap["{}"] = _request._{};\n',
                        field_name,
                        field_name,
                        )
            rpc_block = rpc_block.replace("{{assign}}", assign_block)
        code = template_module_BaseService_cs
        code = code.replace("{{org}}", org_name)
        code = code.replace("{{mod}}", mod_name)
        code = code.replace("{{service}}", service)
        code = code.replace("{{rpc}}", rpc_block)
        wf.write(code)
        wf.close()

# 生成Proto.cs文件
with open("./vs2019/module/Protocol.cs", "w", encoding="utf-8") as wf:
    template_class = r"""
        public class {{message}}
        {
            public {{message}}()
            {
{{assign}}
            }
{{field}}
        }
    """
    proto_block = ""
    for message_name in messages.keys():
        # 成员声明
        field_block = ""
        # 构造函数中赋初值
        assign_block = ""
        # 遍历所有字段
        for field in messages[message_name]:
            # 字段名
            field_name = field[0]
            # 字段类型
            field_type = field[1]
            # 转换枚举类型
            if field_type in enums:
                field_type = "enum"

            if field_type.endswith('[]'):
                field_type = field_type[:-2]
                if field_type in type_dict.keys():
                    """可转换类型的数组, 使用Any转换"""
                    assign_block = assign_block + str.format(
                        "                _{} = Any.From{}Ary(new {}[0]);\n", field_name, field_type.title(), field_type
                        )
                    field_block = field_block + str.format(
                        "            [JsonPropertyName(\"{}\")]\n            public Any _{} {{get;set;}}\n", field_name, field_name
                        )
                else:
                    """不可转换类型的数组, 使用直接实例化的方式"""
                    assign_block = assign_block + str.format(
                        "                _{} = new {}[0];\n", field_name, field_type
                        )
                    field_block = field_block + str.format(
                        "            [JsonPropertyName(\"{}\")]\n            public {}[] _{} {{get;set;}}\n", field_name, field_type, field_name
                        )
            elif field_type.endswith('<>'):
                field_type = field_type[:-2]
                """字典使用直接实例化的方式"""
                assign_block = assign_block + str.format(
                    "                _{} = new Dictionary<string, {}>();\n", field_name, field_type
                    )
                field_block = field_block + str.format(
                    "            [JsonPropertyName(\"{}\")]\n            public Dictionary<string, {}> _{} {{get;set;}}\n", field_name, field_type, field_name
                    )
            else:
                if field_type in type_dict.keys():
                    """可转换类型的数组, 使用Any转换"""
                    csharp_type = type_dict[field_type]
                    any_type = type_to_any[csharp_type]
                    assign_block = assign_block + str.format(
                        "                _{} = Any.From{}({});\n", field_name, any_type.title(), type_default_value[field_type]
                        )
                    field_block = field_block + str.format(
                        "            [JsonPropertyName(\"{}\")]\n            public Any _{} {{get;set;}}\n", field_name, field_name
                        )
                else:
                    """不可转换类型, 使用直接实例化的方式"""
                    assign_block = assign_block + str.format(
                        "                _{} = new {}();\n", field_name, field_type
                        )
                    field_block = field_block + str.format(
                        "            [JsonPropertyName(\"{}\")]\n            public {} _{} {{get;set;}}\n", field_name, field_type, field_name
                        )

        message_block = template_class.replace("{{message}}", message_name)
        message_block = message_block.replace("{{field}}", field_block)
        message_block = message_block.replace("{{assign}}", assign_block)
        proto_block = proto_block + message_block
    code = template_module_Protocol_cs
    code = code.replace("{{org}}", org_name)
    code = code.replace("{{mod}}", mod_name)
    code = code.replace("{{proto}}", proto_block)
    wf.write(code)
    wf.close()

# 生成JsonConvert.cs文件
with open("./vs2019/module/JsonConvert.cs", "w", encoding="utf-8") as wf:
    code = template_module_Json_Convert_cs
    code = code.replace("{{org}}", org_name)
    code = code.replace("{{mod}}", mod_name)
    wf.write(code)
    wf.close()

# 生成JsonOptions.cs文件
with open("./vs2019/module/JsonOptions.cs", "w", encoding="utf-8") as wf:
    code = template_module_Json_Options_cs
    code = code.replace("{{org}}", org_name)
    code = code.replace("{{mod}}", mod_name)
    wf.write(code)
    wf.close()



# -----------------------------------------------------------------------------
# 生成 wpf 解决方案
# -----------------------------------------------------------------------------
os.makedirs("vs2019/wpf", exist_ok=True)
# 生成.proj文件
with open("./vs2019/wpf/wpf.csproj", "w", encoding="utf-8") as wf:
    wf.write(
            template_proj_wpf.replace("{{org}}", org_name).replace("{{mod}}", mod_name)
            )
    wf.close()

# 生成ControlRoot.cs文件
with open("./vs2019/wpf/ControlRoot.cs", "w", encoding="utf-8") as wf:
    template_register_block = r"""
            // 注册UI装饰
            {{service}}Facade facade{{service}} = new {{service}}Facade();
            framework_.getStaticPipe().RegisterFacade({{service}}Facade.NAME, facade{{service}});
            {{service}}Control control{{service}} = new {{service}}Control();
            control{{service}}.facade = facade{{service}};
            {{service}}Control.{{service}}UiBridge ui{{service}}Bridge = new {{service}}Control.{{service}}UiBridge();
            ui{{service}}Bridge.control = control{{service}};
            facade{{service}}.setUiBridge(ui{{service}}Bridge);
        """
    template_cancel_block = r"""
            // 注销UI装饰
            framework_.getStaticPipe().CancelFacade({{service}}Facade.NAME);
        """
    register_block = ""
    cancel_block = ""
    for service in services.keys():
        register_block = register_block + template_register_block.replace(
                "{{service}}", service
                )
        cancel_block = cancel_block + template_cancel_block.replace(
                "{{service}}", service
                )
    code = template_wpf_ControlRoot_cs
    code = code.replace("{{org}}", org_name)
    code = code.replace("{{mod}}", mod_name)
    code = code.replace("{{register}}", register_block)
    code = code.replace("{{cancel}}", cancel_block)
    wf.write(code)
    wf.close()

# 生成Facade.cs文件
for service in services.keys():
    with open(
            "./vs2019/wpf/{}Facade.cs".format(service), "w", encoding="utf-8"
            ) as wf:
        code = template_wpf_Facade_cs
        code = code.replace("{{org}}", org_name)
        code = code.replace("{{mod}}", mod_name)
        code = code.replace("{{service}}", service)
        wf.write(code)
        wf.close()

# 生成Control.cs文件
for service in services.keys():
    with open(
            "./vs2019/wpf/{}Control.xaml.cs".format(service), "w", encoding="utf-8"
            ) as wf:
        code = template_wpf_Control_cs
        code = code.replace("{{org}}", org_name)
        code = code.replace("{{mod}}", mod_name)
        code = code.replace("{{service}}", service)
        wf.write(code)
        wf.close()

# 生成Control.xaml文件
for service in services.keys():
    with open(
            "./vs2019/wpf/{}Control.xaml".format(service), "w", encoding="utf-8"
            ) as wf:
        code = template_wpf_Control_xaml
        code = code.replace("{{org}}", org_name)
        code = code.replace("{{mod}}", mod_name)
        code = code.replace("{{service}}", service)
        wf.write(code)
        wf.close()

