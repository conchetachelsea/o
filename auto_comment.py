import tweepy
import time
from datetime import datetime
import os
import logging
from tweepy import TweepyException

# Masukkan kredensial API Anda
API_KEY = "zBvFMSNZTMCwz8gBIyvxPmai7"
API_SECRET = "kOBv2Y4uHaoMVmZkWBLZktlgJz0QnxUXGXYoymLYT2YOnisSMi"
ACCESS_TOKEN = "1623235054058221574-SFSrIQYB9Y3jXAYfo1Rzqa9M1tT5zC"
ACCESS_TOKEN_SECRET = "fACPwHSt196ibOjnNiRKtwYzt9Nza2wO3w6jh2NhzBxs2"

# Setup logging ke file
logging.basicConfig(
    filename="auto_comment.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()

# Autentikasi dengan Twitter API
try:
    auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)
    api.verify_credentials()  # Verifikasi kredensial saat mulai
    logger.info("Autentikasi berhasil")
except TweepyException as e:
    logger.error(f"Gagal autentikasi: {e}")
    raise SystemExit("Autentikasi gagal, periksa kredensial Anda.")

# Nama file untuk menyimpan ID tweet yang sudah dikomentari
COMMENTED_FILE = "commented_tweets.txt"

# Fungsi untuk memuat ID tweet dari file
def load_commented_tweets():
    commented = set()
    if os.path.exists(COMMENTED_FILE):
        with open(COMMENTED_FILE, "r") as file:
            for line in file:
                tweet_id = line.strip()
                if tweet_id:
                    commented.add(int(tweet_id))
    return commented

# Fungsi untuk menyimpan ID tweet ke file
def save_commented_tweet(tweet_id):
    with open(COMMENTED_FILE, "a") as file:
        file.write(f"{tweet_id}\n")

# Fungsi untuk mencari dan mengomentari postingan dengan retry logic
def auto_comment(keyword, comment_text, max_retries=3):
    commented_tweets = load_commented_tweets()
    logger.info(f"Memuat {len(commented_tweets)} tweet yang sudah dikomentari dari file")

    while True:
        retries = 0
        while retries <= max_retries:
            try:
                # Mencari tweet berdasarkan keyword
                tweets = tweepy.Cursor(api.search_tweets,
                                     q=keyword,
                                     lang="id",
                                     tweet_mode="extended").items(10)
                
                found_new_tweet = False
                
                for tweet in tweets:
                    tweet_id = tweet.id
                    
                    if tweet_id not in commented_tweets:
                        try:
                            username = tweet.user.screen_name
                            comment = f"@{username} {comment_text}"
                            
                            # Mengirim komentar
                            api.update_status(
                                status=comment,
                                in_reply_to_status_id=tweet_id,
                                auto_populate_reply_metadata=True
                            )
                            
                            commented_tweets.add(tweet_id)
                            save_commented_tweet(tweet_id)
                            found_new_tweet = True
                            
                            logger.info(f"Berhasil mengomentari tweet dari @{username} (ID: {tweet_id})")
                            print(f"[{datetime.now()}] Berhasil mengomentari tweet dari @{username}")
                            time.sleep(60)  # Jeda per komentar
                            
                        except TweepyException as e:
                            logger.warning(f"Gagal mengomentari tweet {tweet_id}: {e}")
                            if "429" in str(e):  # Rate limit error
                                logger.info("Rate limit tercapai, menunggu 15 menit...")
                                time.sleep(900)  # Tunggu 15 menit
                            else:
                                time.sleep(60)  # Jeda untuk error lain
                                continue
                
                if not found_new_tweet:
                    logger.info(f"Tidak ada tweet baru dengan keyword '{keyword}'")
                    print(f"[{datetime.now()}] Tidak ada tweet baru, menunggu...")
                
                time.sleep(300)  # Jeda antar iterasi
                break  # Keluar dari retry loop jika sukses
                
            except TweepyException as e:
                retries += 1
                error_code = str(e).split("code")[1].strip("]") if "code" in str(e) else None
                
                if error_code == "429":  # Rate limit
                    logger.warning("Rate limit tercapai, menunggu 15 menit sebelum retry...")
                    time.sleep(900)
                elif error_code in ["401", "403"]:  # Autentikasi atau akses ditolak
                    logger.error(f"Error fatal: {e}. Keluar dari program.")
                    raise SystemExit("Error autentikasi atau akses, periksa kredensial/izin.")
                else:
                    logger.warning(f"Error sementara: {e}. Retry {retries}/{max_retries}")
                    time.sleep(60 * retries)  # Jeda eksponensial
                
                if retries > max_retries:
                    logger.error(f"Gagal setelah {max_retries} percobaan: {e}")
                    print(f"[{datetime.now()}] Gagal setelah {max_retries} percobaan, melanjutkan setelah jeda...")
                    time.sleep(600)  # Jeda panjang sebelum iterasi berikutnya

# Contoh penggunaan
if __name__ == "__main__":
    keyword = "#Python"  # Ganti dengan keyword Anda
    comment_text = "Keren banget postingannya!"  # Ganti dengan komentar Anda
    
    logger.info(f"Memulai auto-comment untuk keyword: {keyword}")
    print(f"[{datetime.now()}] Memulai auto-comment untuk keyword: {keyword}")
    try:
        auto_comment(keyword, comment_text, max_retries=3)
    except KeyboardInterrupt:
        logger.info("Program dihentikan oleh pengguna")
        print(f"[{datetime.now()}] Program dihentikan")
    except Exception as e:
        logger.error(f"Error tak terduga: {e}")
        print(f"[{datetime.now()}] Error tak terduga: {e}")