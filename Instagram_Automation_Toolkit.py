#!/usr/bin/env python3
import os
import json
import time
import random
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired, TwoFactorRequired, BadPassword, UserNotFound, MediaNotFound, ClientError
from instagrapi.types import StoryMention, StoryMedia, StoryLink, StoryHashtag
from datetime import datetime
import schedule

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_ascii_art():
    print(r"""
░▀█▀░█▀█░█▀▀░▀█▀░█▀█░█▀▀░█▀▄░█▀█░█▄█░░░█▀█░█░█░▀█▀░█▀█░█▄█░█▀█░▀█▀░▀█▀░█▀█░█▀█
░░█░░█░█░▀▀█░░█░░█▀█░█░█░█▀▄░█▀█░█░█░░░█▀█░█░█░░█░░█░█░█░█░█▀█░░█░░░█░░█░█░█░█
░▀▀▀░▀░▀░▀▀▀░░▀░░▀░▀░▀▀▀░▀░▀░▀░▀░▀░▀░░░▀░▀░▀▀▀░░▀░░▀▀▀░▀░▀░▀░▀░░▀░░▀▀▀░▀▀▀░▀░▀
""")
    print("\n\x1b[31m" + "Instagram Automation Toolkit" + "\x1b[0m") 
    print("\x1b[31m" + "Powered by AL-MARID" + "\x1b[0m\n") 

class InstagramToolkit:
    def __init__(self):
        self.cl = Client()
        self.settings_path = "instagrapi_settings.json"
        self.scheduled_posts_file = "scheduled_posts.json"
        self.load_settings()
        self.load_scheduled_posts()

    def load_settings(self):
        if os.path.exists(self.settings_path):
            try:
                self.cl.load_settings(self.settings_path)
                print("[+] Session settings loaded successfully.")
            except Exception as e:
                print(f"[!] Failed to load session settings: {e}. Resetting client.")
                self.cl = Client()
        else:
            print("[i] No saved session settings file found. Starting a new session.")

    def dump_settings(self):
        try:
            self.cl.dump_settings(self.settings_path)
            print("[+] Session settings saved successfully.")
        except Exception as e:
            print(f"[!] Failed to save session settings: {e}")

    def load_scheduled_posts(self):
        if os.path.exists(self.scheduled_posts_file):
            with open(self.scheduled_posts_file, 'r') as f:
                self.scheduled_posts = json.load(f)
            print("[+] Scheduled posts loaded successfully.")
        else:
            self.scheduled_posts = []
            print("[i] No scheduled posts file found.")

    def save_scheduled_posts(self):
        with open(self.scheduled_posts_file, 'w') as f:
            json.dump(self.scheduled_posts, f, indent=4)
        print("[+] Scheduled posts saved successfully.")

    def login(self):
        while True:
            login_choice = input("\nChoose login method:\n1. Using Session ID\n2. Using Username and Password\nEnter your choice (1 or 2): ")

            if login_choice == '1':
                session_id = input("Enter your Session ID: ")
                try:
                    self.cl.login_by_sessionid(session_id)
                    print("[+] Logged in successfully using Session ID.")
                    self.dump_settings()
                    return True
                except LoginRequired:
                    print("[!] Invalid or expired Session ID. Please try again.")
                except Exception as e:
                    print(f"[!] An error occurred during login with Session ID: {e}")

            elif login_choice == '2':
                username = input("Enter your username: ")
                password = input("Enter your password: ")
                try:
                    self.cl.login(username, password)
                    print("[+] Logged in successfully using username and password.")
                    self.dump_settings()
                    return True
                except TwoFactorRequired:
                    print("[!] Two-factor authentication required.")
                    code = input("Enter 2FA code: ")
                    try:
                        self.cl.login(username, password, verification_code=code)
                        print("[+] Logged in successfully after 2FA.")
                        self.dump_settings()
                        return True
                    except Exception as e:
                        print(f"[!] 2FA failed: {e}")
                except BadPassword:
                    print("[!] Incorrect password.")
                except UserNotFound:
                    print("[!] Username not found.")
                except ChallengeRequired:
                    print("[!] Security challenge required. Please try logging in manually first or use Session ID.")
                except Exception as e:
                    print(f"[!] An error occurred during login: {e}")
            else:
                print("[!] Invalid choice. Please enter 1 or 2.")
        return False

    def ensure_login(self):
        if not self.cl.user_id:
            print("[i] Not logged in yet.")
            if not self.login():
                print("[!] Login failed. Cannot proceed.")
                return False
        else:
            print("[+] Already logged in.")
            try:
                self.cl.user_info_by_username(self.cl.username)
                print("[+] Current session is valid.")
            except LoginRequired:
                print("[!] Current session expired. Please log in again to continue.")
                if not self.login():
                    print("[!] Login failed. Cannot proceed.")
                    return False
            except Exception as e:
                print(f"[!] An error occurred while verifying session: {e}. Attempting re-login.")
                if not self.login():
                    print("[!] Login failed. Cannot proceed.")
                    return False
        return True

    def set_proxy_settings(self):
        proxy_choice = input("\nDo you want to set Proxy settings? (yes/no): ").lower()
        if proxy_choice == 'yes':
            proxy_dsn = input("Enter proxy address (e.g., socks5://user:pass@host:port or http://host:port): ")
            try:
                self.cl.set_proxy(proxy_dsn)
                print("[+] Proxy set successfully.")
                self.dump_settings()
            except Exception as e:
                print(f"[!] Failed to set proxy: {e}")

    def set_device_settings(self):
        device_choice = input("\nDo you want to set Device and Location settings? (yes/no): ").lower()
        if device_choice == 'yes':
            print("\n[i] You can set Country, Country Code, Locale, and Timezone Offset.")
            country = input("Enter Country code (e.g., US, RU, EG): ") or "US"
            country_code = input("Enter International Dialing Code (e.g., 1 for US, 20 for Egypt): ")
            locale = input("Enter Locale (e.g., en_US, ar_EG): ") or "en_US"
            timezone_offset_str = input("Enter Timezone Offset in seconds (e.g., -25200 for UTC-7): ")

            try:
                if country: self.cl.set_country(country)
                if country_code: self.cl.set_country_code(int(country_code))
                if locale: self.cl.set_locale(locale)
                if timezone_offset_str: self.cl.set_timezone_offset(int(timezone_offset_str))
                print("[+] Device and Location settings set successfully.")
                self.dump_settings()
            except Exception as e:
                print(f"[!] Failed to set device and location settings: {e}")

    def get_user_info(self):
        username = input("Enter username to get info: ")
        try:
            user_id = self.cl.user_id_from_username(username)
            user_info = self.cl.user_info(user_id)
            print("\n--- User Information ---")
            print(f"Username: {user_info.username}")
            print(f"Full Name: {user_info.full_name}")
            print(f"User ID (PK): {user_info.pk}")
            print(f"Followers: {user_info.follower_count}")
            print(f"Following: {user_info.following_count}")
            print(f"Media Count: {user_info.media_count}")
            print(f"Biography: {user_info.biography}")
            private_status = "Yes" if user_info.is_private else "No"
            print(f"Private Account: {private_status}")
            print(f"Verified Account: {'Yes' if user_info.is_verified else 'No'}")
            if user_info.public_email: print(f"Public Email: {user_info.public_email}")
            if user_info.public_phone_number: print(f"Public Phone Number: {user_info.public_phone_number}")
            print("------------------------")
        except UserNotFound:
            print(f"[!] User '{username}' not found.")
        except Exception as e:
            print(f"[!] An error occurred while fetching user info: {e}")

    def get_user_medias(self):
        username = input("Enter username to get their media: ")
        try:
            user_id = self.cl.user_id_from_username(username)
            amount_str = input("Enter number of media to fetch (leave empty for all): ")
            amount = int(amount_str) if amount_str else 0
            medias = self.cl.user_medias(user_id, amount=amount)
            print(f"\n--- Media for user {username} ---")
            if not medias:
                print("No media found.")
                return
            for i, media in enumerate(medias):
                print(f'[{i+1}] Type: {media.media_type.name}, PK: {media.pk}, URL: {media.thumbnail_url}')
                print(f"    Description: {media.caption_text[:50] if media.caption_text else ''}")
                print(f"    Likes: {media.like_count}, Comments: {media.comment_count}")
            print("------------------------")
        except UserNotFound:
            print(f"[!] User '{username}' not found.")
        except Exception as e:
            print(f"[!] An error occurred while fetching user media: {e}")

    def like_media(self):
        media_pk = input("Enter Media PK of the post to like: ")
        try:
            self.cl.media_like(media_pk)
            print(f"[+] Post {media_pk} liked successfully.")
        except MediaNotFound:
            print(f"[!] Post {media_pk} not found.")
        except Exception as e:
            print(f"[!] Failed to like post {media_pk}: {e}")

    def comment_media(self):
        media_pk = input("Enter Media PK of the post to comment on: ")
        comment_text = input("Enter your comment text: ")
        try:
            self.cl.media_comment(media_pk, comment_text)
            print(f"[+] Commented on post {media_pk} successfully.")
        except MediaNotFound:
            print(f"[!] Post {media_pk} not found.")
        except Exception as e:
            print(f"[!] Failed to comment on post {media_pk}: {e}")

    def follow_user(self):
        username = input("Enter username to follow: ")
        try:
            user_id = self.cl.user_id_from_username(username)
            self.cl.user_follow(user_id)
            print(f"[+] User '{username}' followed successfully.")
        except UserNotFound:
            print(f"[!] User '{username}' not found.")
        except Exception as e:
            print(f"[!] Failed to follow user '{username}' : {e}")

    def unfollow_user(self):
        username = input("Enter username to unfollow: ")
        try:
            user_id = self.cl.user_id_from_username(username)
            self.cl.user_unfollow(user_id)
            print(f"[+] User '{username}' unfollowed successfully.")
        except UserNotFound:
            print(f"[!] User '{username}' not found.")
        except Exception as e:
            print(f"[!] Failed to unfollow user '{username}' : {e}")

    def edit_account_bio(self):
        new_bio = input("Enter new biography: ")
        try:
            self.cl.account_edit(biography=new_bio)
            print("[+] Biography updated successfully.")
            self.dump_settings()
        except Exception as e:
            print(f"[!] Failed to update biography: {e}")

    def upload_photo_story(self):
        path = input("Enter the full path to the photo you want to upload as a story: ")
        if not os.path.exists(path):
            print("[!] Invalid path or file does not exist.")
            return
        try:
            self.cl.photo_upload_to_story(path)
            print("[+] Photo uploaded as story successfully.")
        except Exception as e:
            print(f"[!] Failed to upload photo as story: {e}")

    def upload_video_story(self):
        path = input("Enter the full path to the video you want to upload as a story: ")
        if not os.path.exists(path):
            print("[!] Invalid path or file does not exist.")
            return
        try:
            self.cl.video_upload_to_story(path)
            print("[+] Video uploaded as story successfully.")
        except Exception as e:
            print(f"[!] Failed to upload video as story: {e}")

    def send_direct_message(self):
        recipient_username = input("Enter recipient username: ")
        message_text = input("Enter message text: ")
        try:
            recipient_id = self.cl.user_id_from_username(recipient_username)
            self.cl.direct_send(message_text, user_ids=[recipient_id])
            print(f"[+] Message sent to '{recipient_username}' successfully.")
        except UserNotFound:
            print(f"[!] User '{recipient_username}' not found.")
        except Exception as e:
            print(f"[!] Failed to send direct message: {e}")

    def get_account_insights(self):
        try:
            insights = self.cl.account_insights()
            print("\n--- Account Insights ---")
            print(f"Reach: {insights.get('reach')}")
            print(f"Impressions: {insights.get('impressions')}")
            print(f"Profile Views: {insights.get('profile_views')}")
            print("------------------------")
        except Exception as e:
            print(f"[!] Failed to fetch account insights: {e}")

    def get_hashtag_medias(self):
        hashtag_name = input("Enter hashtag name (without #): ")
        try:
            medias = self.cl.hashtag_medias_top(hashtag_name, amount=10)
            print(f"\n--- Top 10 Media for Hashtag #{hashtag_name} ---")
            if not medias:
                print("No media found for this hashtag.")
                return
            for i, media in enumerate(medias):
                print(f'[{i+1}] Type: {media.media_type.name}, PK: {media.pk}, URL: {media.thumbnail_url}')
                print(f"    Description: {media.caption_text[:50] if media.caption_text else ''}")
                print(f"    Likes: {media.like_count}, Comments: {media.comment_count}")
            print("------------------------")
        except Exception as e:
            print(f"[!] Failed to fetch hashtag media: {e}")

    def get_location_medias(self):
        location_name = input("Enter location name: ")
        try:
            locations = self.cl.location_search(location_name)
            if not locations:
                print("[!] No locations found with this name.")
                return
            location_pk = locations[0].pk
            medias = self.cl.location_medias_top(location_pk, amount=10)
            print(f"\n--- Top 10 Media for Location {location_name} ---")
            if not medias:
                print("No media found for this location.")
                return
            for i, media in enumerate(medias):
                print(f'[{i+1}] Type: {media.media_type.name}, PK: {media.pk}, URL: {media.thumbnail_url}')
                print(f"    Description: {media.caption_text[:50] if media.caption_text else ''}")
                print(f"    Likes: {media.like_count}, Comments: {media.comment_count}")
            print("------------------------")
        except Exception as e:
            print(f"[!] Failed to fetch location media: {e}")

    def schedule_post(self):
        media_path = input("Enter the full path to the media file (photo/video) to schedule: ")
        if not os.path.exists(media_path):
            print("[!] Invalid path or file does not exist.")
            return
        caption = input("Enter caption for the post: ")
        schedule_time_str = input("Enter schedule time (YYYY-MM-DD HH:MM): ")
        try:
            schedule_time = datetime.strptime(schedule_time_str, "%Y-%m-%d %H:%M")
            self.scheduled_posts.append({
                "media_path": media_path,
                "caption": caption,
                "schedule_time": schedule_time.isoformat(),
                "posted": False
            })
            self.save_scheduled_posts()
            print(f"[+] Post scheduled successfully for {schedule_time_str}.")
        except ValueError:
            print("[!] Invalid time format. Please use YYYY-MM-DD HH:MM.")
        except Exception as e:
            print(f"[!] Failed to schedule post: {e}")

    def publish_scheduled_posts(self):
        print("[i] Checking for scheduled posts to publish...")
        for post in self.scheduled_posts:
            if not post["posted"] and datetime.fromisoformat(post["schedule_time"]) <= datetime.now():
                print(f"[i] Attempting to publish scheduled post: {post['media_path']}")
                try:
                    if post["media_path"].lower().endswith((".png", ".jpg", ".jpeg")):
                        self.cl.photo_upload(post["media_path"], post["caption"])
                    elif post["media_path"].lower().endswith((".mp4", ".mov")):
                        self.cl.video_upload(post["media_path"], post["caption"])
                    else:
                        print(f"[!] Unsupported media type for {post['media_path']}")
                        continue
                    post["posted"] = True
                    print(f"[+] Scheduled post '{post['media_path']}' published successfully.")
                except LoginRequired:
                    print("[!] Session expired while publishing scheduled post. Please log in again.")
                    break 
                except Exception as e:
                    print(f"[!] Failed to publish scheduled post '{post['media_path']}': {e}")
        self.save_scheduled_posts()

    def auto_dm_on_new_follower(self):
        print("[!] Auto DM on new follower is a complex feature requiring continuous monitoring or webhooks.")
        print("[i] For demonstration, we will simulate sending a DM to a specific user.")
        recipient_username = input("Enter username to send auto DM to (for simulation): ")
        message_text = input("Enter auto DM message: ")
        try:
            recipient_id = self.cl.user_id_from_username(recipient_username)
            self.cl.direct_send(message_text, user_ids=[recipient_id])
            print(f"[+] Simulated auto DM sent to '{recipient_username}' successfully.")
        except UserNotFound:
            print(f"[!] User '{recipient_username}' not found.")
        except Exception as e:
            print(f"[!] Failed to send simulated auto DM: {e}")

    def auto_comment_on_hashtag(self):
        print("[!] Auto Comment on hashtag is a complex feature requiring continuous monitoring or webhooks.")
        print("[i] For demonstration, we will simulate commenting on a specific media.")
        media_pk = input("Enter Media PK of the post to auto comment on (for simulation): ")
        comment_text = input("Enter auto comment text: ")
        try:
            self.cl.media_comment(media_pk, comment_text)
            print(f"[+] Simulated auto comment on post {media_pk} successfully.")
        except MediaNotFound:
            print(f"[!] Post {media_pk} not found.")
        except Exception as e:
            print(f"[!] Failed to send simulated auto comment: {e}")

    def get_enhanced_account_analytics(self):
        try:
            print("\n--- Enhanced Account Analytics (Placeholder) ---")
            print("This feature would provide detailed reports on engagement, best posting times, follower growth, etc.")
            print("Currently displaying basic insights:")
            self.get_account_insights()
            print("------------------------------------------------")
        except Exception as e:
            print(f"[!] Failed to fetch enhanced analytics: {e}")

    def display_menu(self):
        print("\n--- Instagram Toolkit Menu ---")
        print("1. Login / Verify Session")
        print("2. Set Proxy Settings")
        print("3. Set Device and Location Settings")
        print("4. Get User Information")
        print("5. Get User Media")
        print("6. Like Media")
        print("7. Comment on Media")
        print("8. Follow User")
        print("9. Unfollow User")
        print("10. Edit Account Bio")
        print("11. Upload Photo Story")
        print("12. Upload Video Story")
        print("13. Send Direct Message")
        print("14. Get Account Insights (Business/Creator Account)")
        print("15. Get Top Media for a Hashtag")
        print("16. Get Top Media for a Location")
        print("17. Schedule Post")
        print("18. Publish Scheduled Posts (Run this periodically)")
        print("19. Auto DM on New Follower")
        print("20. Auto Comment on Hashtag")
        print("21. Get Enhanced Account Analytics")
        print("0. Exit")

    def run(self):
        clear_screen()
        display_ascii_art()
        if not self.ensure_login():
            return

        while True:
            self.display_menu()
            choice = input("Enter your choice: ")

            if choice == '1':
                self.ensure_login()
            elif choice == '2':
                self.set_proxy_settings()
            elif choice == '3':
                self.set_device_settings()
            elif choice == '4':
                self.get_user_info()
            elif choice == '5':
                self.get_user_medias()
            elif choice == '6':
                self.like_media()
            elif choice == '7':
                self.comment_media()
            elif choice == '8':
                self.follow_user()
            elif choice == '9':
                self.unfollow_user()
            elif choice == '10':
                self.edit_account_bio()
            elif choice == '11':
                self.upload_photo_story()
            elif choice == '12':
                self.upload_video_story()
            elif choice == '13':
                self.send_direct_message()
            elif choice == '14':
                self.get_account_insights()
            elif choice == '15':
                self.get_hashtag_medias()
            elif choice == '16':
                self.get_location_medias()
            elif choice == '17':
                self.schedule_post()
            elif choice == '18':
                self.publish_scheduled_posts()
            elif choice == '19':
                self.auto_dm_on_new_follower()
            elif choice == '20':
                self.auto_comment_on_hashtag()
            elif choice == '21':
                self.get_enhanced_account_analytics()
            elif choice == '0':
                print("Exiting Instagram Toolkit. Goodbye!")
                break
            else:
                print("[!] Invalid choice. Please try again.")
            input("Press Enter to continue...")
            clear_screen()
            display_ascii_art()

if __name__ == "__main__":
    toolkit = InstagramToolkit()
    toolkit.run()

