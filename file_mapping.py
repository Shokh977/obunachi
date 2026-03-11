# File ID to Telegram Post URL Mapping
# Format: file_id -> telegram post URL
# Example: https://t.me/channel_name/post_number

FILE_MAPPING = {
    "1": "https://t.me/kanalingiz_yuzeri/100",
    "2": "https://t.me/kanalingiz_yuzeri/101",
    "3": "https://t.me/kanalingiz_yuzeri/102",
    "4": "https://t.me/kanalingiz_yuzeri/103",
    "5": "https://t.me/kanalingiz_yuzeri/104",
}

def get_post_url(file_id):
    """Get Telegram post URL by file_id"""
    return FILE_MAPPING.get(file_id, None)
