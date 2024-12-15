import os
import time
import json
import requests
import pdfplumber
import pandas as pd
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import platform
from plyer import notification

# Android specific imports
if platform == 'android':
    from jnius import autoclass
    PythonService = autoclass('org.kivy.android.PythonService')
    Intent = autoclass('android.content.Intent')
    mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
    Environment = autoclass('android.os.Environment')
    File = autoclass('java.io.File')

# 配置文件夹路径（修改为 Android 存储路径）
if platform == 'android':
    # Get the Downloads directory using Android's storage framework
    downloads_dir = Environment.getExternalStoragePublicDirectory(
        Environment.DIRECTORY_DOWNLOADS
    ).getAbsolutePath()
    WATCH_FOLDER = downloads_dir
    # Use app's private storage for config
    CONFIG_PATH = os.path.join(
        mActivity.getFilesDir().getAbsolutePath(),
        "config.json"
    )
else:
    WATCH_FOLDER = os.path.expanduser("~/Downloads")
    CONFIG_PATH = "config.json"

# 登录接口地址
LOGIN_URL = "https://aiforoptometry.com/jtlogin/verif"

# 全局组织信息
organization_data = {
    "organizationId": None,
    "organizationName": None
}

# 本地配置文件路径
CONFIG_PATH = "config.json"

class LoginScreen(BoxLayout):
    def __init__(self, callback, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.callback = callback

        # 登录界面布局
        self.add_widget(Label(text="请输入账号:", font_name="msyh.ttc"))
        self.username_input = TextInput(multiline=False)
        self.add_widget(self.username_input)

        self.add_widget(Label(text="请输入密码:", font_name="msyh.ttc"))
        self.password_input = TextInput(password=True, multiline=False)
        self.add_widget(self.password_input)

        submit_button = Button(text="提交", font_name="msyh.ttc")
        submit_button.bind(on_press=self.validate_credentials)
        self.add_widget(submit_button)

    def validate_credentials(self, instance):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()

        try:
            response = requests.post(LOGIN_URL, json={"username": username, "password": password})
            print(f"服务器返回内容: {response.text}")

            if response.status_code == 200:
                response_json = response.json()
                # 检查是否包含 'success' 并确认登录成功
                if response_json.get("success") == "Login successful":
                    organization_data["organizationId"] = response_json["organization_id"]
                    organization_data["organizationName"] = response_json["organization_name"]

                    # 保存配置到本地文件
                    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                        json.dump(organization_data, f, indent=4, ensure_ascii=False)

                    self.callback(success=True)
                else:
                    notification.notify(
                        title="登录失败",
                        message="登录返回信息异常，请检查账号或密码。",
                        timeout=5
                    )
            else:
                notification.notify(
                    title="登录失败",
                    message=f"服务器返回错误，状态码: {response.status_code}",
                    timeout=5
                )
        except Exception as e:
            notification.notify(
                title="网络错误",
                message=f"无法连接到登录接口: {e}",
                timeout=5
            )


class WelcomeScreen(BoxLayout):
    def __init__(self, organization_data, logout_callback, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.logout_callback = logout_callback

        # 欢迎消息
        self.add_widget(Label(text="欢迎登陆", font_name="msyh.ttc"))
        self.add_widget(Label(text=f"组织ID: {organization_data['organizationId']}", font_name="msyh.ttc"))

        # 退出按钮
        logout_button = Button(text="退出登陆", font_name="msyh.ttc")
        logout_button.bind(on_press=self.logout)
        self.add_widget(logout_button)

    def logout(self, instance):
        self.logout_callback()



class PDFHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".pdf"):
            print(f"检测到新文件: {event.src_path}")
            pdf_file = event.src_path

            # 等待文件写入完成
            if not self.wait_for_file(pdf_file):
                print(f"文件 {pdf_file} 写入未完成或无法访问，跳过处理。")
                return

            try:
                excel_file = self.pdf_to_excel(pdf_file)
                self.excel_to_json(excel_file)
                print(f"处理完成，文件已生成: {excel_file}")
            except Exception as e:
                print(f"处理文件 {pdf_file} 时发生错误: {e}")

    def wait_for_file(self, file_path, timeout=10):
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                with open(file_path, 'rb'):
                    return True
            except (OSError, PermissionError):
                time.sleep(0.5)
        return False

    def pdf_to_excel(self, pdf_file):
        # 定义生成的 Excel 文件路径
        excel_file = pdf_file.replace(".pdf", ".xlsx")
        try:
            with pdfplumber.open(pdf_file) as pdf:
                page = pdf.pages[0]  # 假设只有一页

                # 定义前三个表格的区域范围 (0~302)
                left_bbox = (0, 0, 302, page.height)
                left_part = page.within_bbox(left_bbox)
                left_text = left_part.extract_text()
                left_lines = left_text.split("\n") if left_text else []

                # 定义第四个表格的区域范围 (435~498)
                right_bbox = (373, 0, 498, page.height)
                right_part = page.within_bbox(right_bbox)
                right_text = right_part.extract_text()
                right_lines = right_text.split("\n") if right_text else []

                # 初始化表格列表
                table_1, table_2, table_3, table_4 = [], [], [], []
                current_table = None

                # 处理前三个表格
                for line in left_lines:
                    if "验光报告" in line:
                        current_table = table_1
                    elif "SubJ" in line:
                        current_table = table_2
                    elif "Final" in line:
                        current_table = table_3

                    if current_table is not None:
                        current_table.append(line)

                # 处理第四个表格
                for line in right_lines:
                    if "试项" in line:
                        current_table = table_4

                    if current_table is not None:
                        table_4.append(line)

                # 转换为 DataFrame
                dataframes = []
                for table in [table_1, table_2, table_3, table_4]:
                    table_data = [row.split() for row in table if isinstance(row, str) and row.strip()]
                    df = pd.DataFrame(table_data)
                    dataframes.append(df)

                # 保存到 Excel 多个 Sheet
                with pd.ExcelWriter(excel_file) as writer:
                    for idx, df in enumerate(dataframes):
                        sheet_name = f"Sheet{idx + 1}"
                        df.to_excel(writer, index=False, header=False, sheet_name=sheet_name)

            print(f"PDF 已转换为 Excel 并保存: {excel_file}")
        except Exception as e:
            print(f"PDF 转换为 Excel 时发生错误: {e}")
            raise
        return excel_file



    def excel_to_json(self, excel_file):
        try:
            # 读取 Excel 文件的所有 Sheet
            sheet_data = pd.read_excel(excel_file, sheet_name=None, header=None)
            flat_json = {}

            def safe_get(row, col):
                """安全获取单元格值，将 None、NaN、N/A 等替换为空字符串，并强制转换为字符串"""
                value = df.iloc[row, col] if len(df) > row and len(df.columns) > col else None
                if pd.isna(value) or value in [None, "N/A", "null", float('nan')]:
                    return ""
                return str(value)

            def parse_bo_bi(value):
                """解析 BO/BI 值"""
                if not value or (not value.startswith("BO") and not value.startswith("BI")):
                    return ""
                sign = "+" if value.startswith("BO") else "-"
                number = value[2:]  # 提取数字部分
                return f"{sign}{number}"

            # 遍历每个 Sheet
            for sheet_name, df in sheet_data.items():
                if sheet_name == "Sheet1":
                    # 提取 Sheet1 的特定值
                    flat_json["id"] = safe_get(3, 1)  # B4

                elif sheet_name == "Sheet2":
                    # 提取 Sheet2 的特定值
                    flat_json["subjective_right_spherical"] = safe_get(2, 1)  # B3
                    flat_json["subjective_right_cylindrical"] = safe_get(3, 1)  # B4
                    flat_json["subjective_right_axis"] = safe_get(4, 1)  # B5

                    flat_json["subjective_left_spherical"] = safe_get(2, 2)  # C3
                    flat_json["subjective_left_cylindrical"] = safe_get(3, 2)  # C4
                    flat_json["subjective_left_axis"] = safe_get(4, 2)  # C5

                    flat_json["near_subjective_right_spherical"] = safe_get(2, 3)  # D3
                    flat_json["near_subjective_right_cylindrical"] = safe_get(3, 3)  # D4
                    flat_json["near_subjective_right_axis"] = safe_get(4, 3)  # D5

                    flat_json["near_subjective_left_spherical"] = safe_get(2, 4)  # E3
                    flat_json["near_subjective_left_cylindrical"] = safe_get(3, 4)  # E4
                    flat_json["near_subjective_left_axis"] = safe_get(4, 4)  # E5

                    flat_json["subjective_right_near_add_power"] = safe_get(9, 1)  # B10
                    flat_json["subjective_left_near_add_power"] = safe_get(9, 2)  # C10

                    flat_json["subjective_right_old_vision"] = safe_get(10, 1)  # B11
                    flat_json["subjective_left_old_vision"] = safe_get(10, 2)  # C11
                    flat_json["near_subjective_right_old_vision"] = safe_get(10, 3)  # D11
                    flat_json["near_subjective_left_old_vision"] = safe_get(10, 4)  # E11

                    # A12 判断逻辑
                    a12_value = safe_get(11, 0)  # A12
                    if a12_value != "PD":
                        flat_json["subjective_both_old_vision"] = a12_value  # A12
                        flat_json["near_subjective_both_old_vision"] = safe_get(11, 1)  # B12
                        flat_json["subjective_both_pupil_distance"] = safe_get(12, 1)  # B13
                        flat_json["near_subjective_both_pupil_distance"] = safe_get(12, 2)  # C13
                    else:
                        flat_json["subjective_both_pupil_distance"] = safe_get(11, 1)  # B12
                        flat_json["near_subjective_both_pupil_distance"] = safe_get(11, 2)  # C12

                elif sheet_name == "Sheet3":
                    # 提取 Sheet3 的特定值
                    flat_json["vacc_right_spherical"] = safe_get(2, 1)  # B3
                    flat_json["vacc_right_cylindrical"] = safe_get(3, 1)  # B4
                    flat_json["vacc_right_axis"] = safe_get(4, 1)  # B5

                    flat_json["vacc_left_spherical"] = safe_get(2, 2)  # C3
                    flat_json["vacc_left_cylindrical"] = safe_get(3, 2)  # C4
                    flat_json["vacc_left_axis"] = safe_get(4, 2)  # C5

                    flat_json["near_vacc_right_spherical"] = safe_get(2, 3)  # D3
                    flat_json["near_vacc_right_cylindrical"] = safe_get(3, 3)  # D4
                    flat_json["near_vacc_right_axis"] = safe_get(4, 3)  # D5

                    flat_json["near_vacc_left_spherical"] = safe_get(2, 4)  # E3
                    flat_json["near_vacc_left_cylindrical"] = safe_get(3, 4)  # E4
                    flat_json["near_vacc_left_axis"] = safe_get(4, 4)  # E5

                    flat_json["vacc_right_old_vision"] = safe_get(10, 1)  # B11
                    flat_json["vacc_left_old_vision"] = safe_get(10, 2)  # C11
                    flat_json["near_vacc_right_old_vision"] = safe_get(10, 3)  # D11
                    flat_json["near_vacc_left_old_vision"] = safe_get(10, 4)  # E11

                    # A12 判断逻辑
                    a12_value = safe_get(11, 0)  # A12
                    if a12_value != "PD":
                        flat_json["vacc_both_old_vision"] = a12_value  # A12
                        flat_json["near_vacc_both_old_vision"] = safe_get(11, 1)  # B12
                        flat_json["vacc_both_pupil_distance"] = safe_get(12, 1)  # B13
                        flat_json["near_vacc_both_pupil_distance"] = safe_get(12, 2)  # C13
                    else:
                        flat_json["vacc_both_pupil_distance"] = safe_get(11, 1)  # B12
                        flat_json["near_vacc_both_pupil_distance"] = safe_get(11, 2)  # C12

                elif sheet_name == "Sheet4":
                    # 提取 Sheet4 的特定值
                    field_mapping = {
                        3: "stereopsis_testing",
                        5: "plo_eso_distance_lateral_phoria",
                        6: "fusional_disvergence_distance_blur",
                        7: "fusional_disvergence_distance_break",
                        8: "fusional_disvergence_distance_recovery",
                        9: "fusional_convergence_distance_blur",
                        10: "fusional_convergence_distance_break",
                        11: "fusional_convergence_distance_recovery",
                        12: "plo_eso_near_lateral_phoria",
                        13: "fusional_disvergence_near_blur",
                        14: "fusional_disvergence_near_break",
                        15: "fusional_disvergence_near_recovery",
                        16: "fusional_convergence_near_blur",
                        17: "fusional_convergence_near_break",
                        18: "fusional_convergence_near_recovery",
                        19: "AC_A",
                        20: "near_point_of_convergence_distance",
                        21: "near_point_of_convergence_ma",
                        22: "near_point_of_convergence_prism",
                        23: "right_near_point_of_accommodation_diopters",
                        24: "near_point_of_accommodation_diopters",
                        25: "left_near_point_of_accommodation_diopters",
                        28: "negative_relative_accommodation_blur",
                        29: "negative_relative_accommodation_recovery",
                        34: "positive_relative_accommodation_blur",
                        35: "positive_relative_accommodation_recovery",
                    }
                    for row, field_name in field_mapping.items():
                        value = safe_get(row - 1, 1)  # B列 (行号-1)
                        if row in [5, 12] and ("BO" in value or "BI" in value):
                            flat_json[field_name] = parse_bo_bi(value)
                        else:
                            flat_json[field_name] = value
            # 添加全局组织信息
            flat_json.update({
                "organizationId": organization_data["organizationId"],
                "organizationName": organization_data["organizationName"],
                # 动态生成 gkid
                "gkid": f"{organization_data['organizationName']}{flat_json.get('id', '')}"
            })

            # 保存 JSON 数据为文件
            json_file = excel_file.replace(".xlsx", ".json")
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(flat_json, f, indent=4, ensure_ascii=False)

            print(f"JSON 数据已生成: {json_file}")
            print("以下是生成的 JSON 数据:")
            print(json.dumps(flat_json, indent=4, ensure_ascii=False))
        except Exception as e:
            print(f"Excel 转换为 JSON 时发生错误: {e}")
            raise



class PDFApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logged_in = False
        self.observer = None
        self.main_screen = None
        # Request permissions on Android
        if platform == 'android':
            from permissions import check_and_request_permissions
            if not check_and_request_permissions():
                notification.notify(
                    title="权限错误",
                    message="无法获取必要权限，应用可能无法正常工作",
                    timeout=5
                )

    def build(self):
        self.start_service()

        # 尝试自动登录
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                saved_data = json.load(f)
                organization_data.update(saved_data)
                self.logged_in = True
                notification.notify(
                    title="自动登录成功",
                    message=f"组织: {saved_data['organizationName']}，开始监听文件夹。",
                    timeout=5
                )
                return self.show_main_screen()

        # 如果自动登录失败，显示登录界面
        self.login_screen = LoginScreen(callback=self.on_login)
        return self.login_screen

    def on_login(self, success):
        if success:
            notification.notify(
                title="登录成功",
                message="程序将最小化并自动开始监听文件夹。",
                timeout=5
            )
            self.logged_in = True
            self.show_main_screen()
            Window.minimize()
        else:
            notification.notify(
                title="登录失败",
                message="账号或密码错误，请重试。",
                timeout=5
            )

    def show_main_screen(self):
        """
        显示主界面，包含文件夹监听状态及退出登录按钮
        """
        if not self.main_screen:
            self.main_screen = BoxLayout(orientation='vertical')

            # 欢迎消息
            self.main_screen.add_widget(Label(
                text=f"欢迎登录！组织: {organization_data.get('organizationName', '未知')}",
                font_name="msyh.ttc"
            ))

            # 监听文件夹状态
            self.main_screen.add_widget(Label(
                text=f"监听文件夹: {WATCH_FOLDER}",
                font_name="msyh.ttc"
            ))

            # 退出登录按钮
            logout_button = Button(text="退出登录", font_name="msyh.ttc")
            logout_button.bind(on_press=self.logout)
            self.main_screen.add_widget(logout_button)

        self.start_watching()
        return self.main_screen

    def logout(self, instance):
        """
        退出登录，清理状态并返回到登录界面
        """
        self.logged_in = False
        self.stop_watching()
        if os.path.exists(CONFIG_PATH):
            os.remove(CONFIG_PATH)
        notification.notify(
            title="已退出登录",
            message="您已成功退出登录，请重新登录。",
            timeout=5
        )
        self.root.clear_widgets()
        self.login_screen = LoginScreen(callback=self.on_login)
        self.root.add_widget(self.login_screen)

    def start_watching(self):
        if platform == 'android':
            from permissions import check_and_request_permissions
            if not check_and_request_permissions():
                notification.notify(
                    title="权限错误",
                    message="无法获取存储权限，文件监控功能将无法使用",
                    timeout=5
                )
                return

        if not os.path.exists(WATCH_FOLDER):
            os.makedirs(WATCH_FOLDER)

        try:
            print(f"开始监听文件夹: {WATCH_FOLDER}")
            event_handler = PDFHandler()
            self.observer = Observer()
            self.observer.schedule(event_handler, WATCH_FOLDER, recursive=False)
            self.observer.start()

            notification.notify(
                title="监听器启动",
                message="监听器已成功启动。",
                timeout=5
            )
        except Exception as e:
            notification.notify(
                title="监听启动失败",
                message=f"原因：{e}",
                timeout=5
            )

    def stop_watching(self):
        """
        停止文件夹监听
        """
        try:
            print("停止监听文件夹")
            if self.observer:
                self.observer.stop()
                self.observer.join()
            notification.notify(
                title="监听器停止",
                message="监听器已停止。",
                timeout=5
            )
        except Exception as e:
            print(f"停止监听器时发生错误: {e}")

    def start_service(self):
        """Start the PDF monitor service"""
        if platform == 'android':
            try:
                service = PythonService.mService
                if not service:
                    service = autoclass('org.kivy.android.PythonService')
                    service.start('PDF处理服务', 'service.py')
                    notification.notify(
                        title="服务启动",
                        message="后台服务已启动！",
                        timeout=5
                    )
            except Exception as e:
                notification.notify(
                    title='服务启动失败',
                    message=f'无法启动PDF监控服务: {str(e)}',
                    timeout=5
                )
        else:
            try:
                subprocess.Popen(["python", "service.py"], shell=True)
                notification.notify(
                    title="服务启动",
                    message="后台服务已启动！",
                    timeout=5
                )
            except Exception as e:
                notification.notify(
                    title='服务启动失败',
                    message=f'无法启动PDF监控服务: {str(e)}',
                    timeout=5
                )

    def on_stop(self):
        """Clean up on app close"""
        self.stop_watching()
        if platform == 'android':
            try:
                service_intent = Intent(mActivity, PythonService)
                mActivity.stopService(service_intent)
            except Exception as e:
                print(f"Error stopping service: {str(e)}")
        super().on_stop()


if __name__ == "__main__":
    PDFApp().run()


