#!/usr/bin/env python3
from instagrapi import Client
import random
import time
import os
import json

target_usernames = [
    "mohamed_salah", "nancyajram", "elissazkh", "amrdiab", "haifawehbe",
    "ahmedhelmy", "assala_official", "sherine", "tamerhosny", "raghebalama",
    "aboflah", "cristiano", 
    "balqeesfathi", "saadlamjarred1", "hendsabri", "ghadaabdelrazek", "youssef_elsharif",
    "cyrineanour", "carole_samaha", "wael_kfoury", "najwakaram", "kazem_ch_official",
    "latifaofficial", "saberrebai", "marwankhoury", "melhemzein", "ziadbourji",
    "maya_diab", "nawalelzoghbi", "fareskaram", "josephattieh", "myriamfares",
    "nassifzeytoun", "adham_nabulsi", "mohammedassaf89", "hanyramzy", "ahmedfahmy_official",
    "karimfahmyofficial", "aytenamer", "maiomar_", "dorra_zarrouk", "mennainstagram",
    "yasmine_sabri", "ghada_adel_official", "ruby_official", "shereenredaofficial", "nesrinet_official",
    "bassemyoussef", "ramiayach", "rasha_rizk", "samer_al_masri", "kindaalloush",
    "abed.fahed", "nadine.nassib.njeim", "timhassan", "valerieabouchacra", "maguyboughosn",
    "dalida_khalil", "stephanieatalaofficial", "daniellabouhamad", "joellembc1", "hishamhaddadofficial",
    "adelkaram", "georgeskhabbaz", "fouad_yammine", "carlahaddadofficial", "rita_harb",
    "dima_sadek", "marcelghanem", "tonybaroud", "zuhairmuradprivate", "eliesaabworld",
    "georgeshobeika", "rabihkeyrouz", "hassanhajjar", "reem_acra", "rami.kadi",
    "zayn", "gigihadid", "bellahadid", "salmahayek", "ramimalek",
    "djkhaled", "riyadmahrez26.7", "achrafhakimi", "yassine_bounou",
    "hakimziyech", "sofyanamrabat", "ismaelben_nacer", "kalidou_koulibaly", "sadio_mane",
    "mohamedelneny", "trezeguet", "mostafamohamed", "ahmedhegazy", "tareqhamed",
    "abdallah_elsaid", "ramadansobhi", "kahraba", "waledsoliman", "amr_w_arda"
]

arabic_message = "مرحباً! أردت فقط أن أقول أنني أقدر المحتوى الذي تقدمه. أتمنى لك يوماً رائعاً!"

def login_to_instagram(sessionid):
    cl = Client()
    settings_file = "instagrapi.json"
    
    print(f"[INFO] Attempting to log in with session ID: {sessionid}")

    try:
        cl.set_settings({"sessionid": sessionid})
        cl.login_by_sessionid(sessionid)
        cl.dump_settings(settings_file) 
        user_info = cl.account_info()
        print(f"[SUCCESS] Logged in as @{user_info.username} (User ID: {user_info.pk})")
        print(f"[INFO] Login API endpoint: https://i.instagram.com/api/v1/accounts/login/")
    except Exception as e:
        print(f"[CRITICAL ERROR] Login failed with session ID: {sessionid}. Error: {e}")
        print(f"[INFO] Login API endpoint: https://i.instagram.com/api/v1/accounts/login/")
        raise 
    return cl

def send_message_to_target_users(cl, message, users_list):
    print("[INFO] Starting to send messages to target users...")
    sent_users = set() 
    for username in users_list:
        if username in sent_users:
            print(f"[INFO] Skipping @{username}, message already sent in this session.")
            continue
        try:
            print(f"[INFO] Attempting to get user ID for @{username}")
            user_info = cl.user_info_by_username(username)
            user_id = user_info.pk
            user_profile_url = f"https://www.instagram.com/{username}/"
            print(f"[SUCCESS] Found user @{username} (ID: {user_id}) from profile URL: {user_profile_url}")
            print(f"[INFO] User info API endpoint: https://i.instagram.com/api/v1/users/{user_id}/info/")
            
            print(f"[INFO] Attempting to send message to @{username} (ID: {user_id})")
            cl.direct_send(message, user_ids=[user_id])
            print(f"[SUCCESS] Sent message to @{username} successfully.")
            print(f"[INFO] Direct message API endpoint: https://i.instagram.com/api/v1/direct_v2/threads/broadcast/text/")
            sent_users.add(username)
            time.sleep(random.randint(10, 20))
        except TypeError as te:
            print(f"[ERROR] Failed to get user info for @{username} due to API response issue (TypeError): {te}")
            print(f"[INFO] This often indicates an intermittent issue with Instagram's API response or 'Content-Length' header.")
            print(f"[INFO] User info API endpoint (if failed to get ID): https://i.instagram.com/api/v1/users/web_profile_info/?username={username}")
        except Exception as e:
            print(f"[ERROR] Failed to send message to @{username}. Error: {e}")
            print(f"[INFO] User info API endpoint (if failed to get ID): https://i.instagram.com/api/v1/users/web_profile_info/?username={username}")
            print(f"[INFO] Direct message API endpoint (if failed to send): https://i.instagram.com/api/v1/direct_v2/threads/broadcast/text/")
    print("[INFO] Finished sending messages to all target users.")

def main():
    sessionid = input("Please enter your Instagram session ID: ")
    try:
        cl = login_to_instagram(sessionid)
    except Exception as e:
        print(f"[CRITICAL ERROR] Script terminated due to login failure.")
        return

    send_message_to_target_users(cl, arabic_message, target_usernames)
    print("[INFO] Script finished execution.")

if __name__ == "__main__":
    main()


