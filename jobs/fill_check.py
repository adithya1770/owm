from client import supabase

def fill_check():
    bins = supabase.table("bins").select("bin_id, fill_level, fill_level_max, status").execute().data
    for bin in bins:
        if bin["fill_level"] >= bin["fill_level_max"]:
            supabase.table("bins").update({"status": "filled"}).eq("bin_id", bin["bin_id"]).execute()
