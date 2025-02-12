import pyautogui
import keyboard
import time
from datetime import datetime
def auto_actions():
    """
    自动操作程序:
    1. 按F10开始/暂停连续鼠标点击
    2. 每5分钟自动按一次F5键
    """
    is_clicking = False
    last_f5_time = time.time()
    F5_INTERVAL = 600  # 5分钟 = 300秒
    
    def toggle_clicking():
        nonlocal is_clicking
        is_clicking = not is_clicking
        status = "启动" if is_clicking else "暂停"
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 自动点击已{status}")
    
    print("自动操作程序已就绪!")
    print("按 F10 开始/暂停自动点击")
    print("每10分钟会自动按一次F5键")
    print("按 Ctrl+C 可以退出程序")
    
    # 注册F10热键
    keyboard.on_press_key('F10', lambda _: toggle_clicking())
    
    try:
        while True:
            current_time = time.time()
            
            # 处理自动点击
            # if is_clicking:
            #     pyautogui.click()
            #     print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 已点击鼠标左键", end='\r')
            
            # 处理F5按键
            if current_time - last_f5_time >= F5_INTERVAL:
                pyautogui.press('f5')
                # print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 已按下F5键")
                last_f5_time = current_time
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n程序已被用户终止")
    except Exception as e:
        print(f"\n发生错误: {str(e)}")
    finally:
        # 清理键盘监听器
        keyboard.unhook_all()

if __name__ == "__main__":
    auto_actions()