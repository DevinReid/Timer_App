import winreg
import struct

def get_system_font():
    try:
        # Open the registry key for desktop appearance settings
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Control Panel\Desktop\WindowMetrics"
        )
        
        # Query the 'CaptionFont' value
        font_data, _ = winreg.QueryValueEx(key, "CaptionFont")

        # The font name starts at a fixed offset (usually 28 bytes into the binary data)
        # and ends at the first null character (\x00).
        font_name_bytes = font_data[28:]  # Extract the font name part
        font_name = font_name_bytes.split(b'\x00')[0].decode("utf-8")  # Decode until null character

        return font_name
    except Exception as e:
        return f"Error: {e}"

# Get the current system font
current_font = get_system_font()
print(f"Current System Default Font: {current_font}")
