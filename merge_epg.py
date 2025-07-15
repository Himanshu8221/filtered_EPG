import os
import xml.etree.ElementTree as ET
import requests
import gzip
import shutil

print("🔧 Starting EPG merge and filter process...")

# ✅ List all channel IDs you want (as strings)
target_channel_ids = {"8", "51", "61", "1470", "52"}

# ✅ Collect all EPG URLs from env
epg_urls = [os.getenv(f"EPG_URL_{i}") for i in range(1, 6) if os.getenv(f"EPG_URL_{i}")]
if not epg_urls:
    print("❌ No EPG_URL_X environment variables found.")
    exit(1)

# ✅ Download and extract each .gz file
def download_and_extract(url, xml_path, gz_path):
    try:
        print(f"➡️ Downloading: {url}")
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        with open(gz_path, "wb") as f:
            f.write(r.content)
        with gzip.open(gz_path, "rb") as f_in:
            with open(xml_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        print(f"✅ Extracted to: {xml_path}")
    except Exception as e:
        print(f"❌ Error downloading {url}: {e}")

# ✅ Merge all XML trees into one
def merge_epg_sources(xml_paths):
    merged_root = ET.Element("tv")
    for path in xml_paths:
        try:
            tree = ET.parse(path)
            root = tree.getroot()
            for elem in root:
                merged_root.append(elem)
            print(f"✅ Merged: {path}")
        except Exception as e:
            print(f"❌ Failed to parse {path}: {e}")
    return merged_root

# ✅ Filter merged EPG
def filter_epg(root, output_path):
    new_root = ET.Element("tv")
    added_channels = 0
    added_programmes = 0

    for channel in root.findall(".//channel"):
        if channel.get("id") in target_channel_ids:
            new_root.append(channel)
            added_channels += 1

    for programme in root.findall(".//programme"):
        if programme.get("channel") in target_channel_ids:
            new_root.append(programme)
            added_programmes += 1

    ET.ElementTree(new_root).write(output_path, encoding="utf-8", xml_declaration=True)
    print(f"✅ Filtered: {added_channels} channels, {added_programmes} programmes")
    print(f"💾 Saved to: {output_path}")

# ✅ Orchestrate the full process
xml_paths = []
for i, url in enumerate(epg_urls, start=1):
    gz_path = f"epg{i}.xml.gz"
    xml_path = f"epg{i}.xml"
    download_and_extract(url, xml_path, gz_path)
    xml_paths.append(xml_path)

print("🔀 Merging sources...")
merged = merge_epg_sources(xml_paths)

print("🔍 Filtering merged EPG...")
filter_epg(merged, "filtered_epg.xml")
