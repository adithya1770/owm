import requests, random
from client import supabase
import time

def call_bin():
    bins = supabase.table("bins").select("bin_id", "fill_level", "status").execute().data

    id_array = [int(bin_["bin_id"]) for bin_ in bins]

    bin_id = random.choice(id_array)

    current_bin = supabase.table("bins").select("fill_level").eq("bin_id", bin_id).execute().data[0]
    current_fill = current_bin["fill_level"]

    if bins["status"] == "not filled":
        supabase.table("bins").update({"fill_level": current_fill + 5}).eq("bin_id", bin_id).execute()
    else:
        print("Bin is already filled.")
    print("Bin Updated!")

    time.sleep(10)
