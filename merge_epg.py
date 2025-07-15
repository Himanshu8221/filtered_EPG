import os
import xml.etree.ElementTree as ET
import requests
import gzip
import shutil

print("🔧 Starting EPG filter process...")

# Step 1: Read EPG URL from environment variable
epg_url = os.getenv("EPG_URL_1")

print("📥 Checking environment variable...")
if not epg_url:
    print("❌ EPG_URL_1 is missing.")
    exit(1)

# ✅ Step 2: Set channel IDs to keep
target_channel_ids = {"8"}  # <- You can add more like "8", "51", etc.

# Step 3: Download and extract .gz to .xml
def download_and_extract(url, out_xml, temp_gz):
    try:
        print(f"➡️ Downloading from: {url}")
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        with open(temp_gz, 'wb') as f:
            f.write(r.content)
        print(f"✅ Downloaded: {temp_gz}")

        with gzip.open(temp_gz, 'rb') as f_in:
            with open(out_xml, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        print(f"📂 Extracted to: {out_xml}")
    except Exception as e:
        print(f"❌ Failed to download or extract {url}: {e}")
        exit(1)

# Step 4: Filter EPG by channel ID
def filter_epg_by_channel_id(input_xml, output_xml):
    try:
        print(f"📂 Parsing EPG file: {input_xml}")
        tree = ET.parse(input_xml)
        root = tree.getroot()

        new_root = ET.Element('tv')
        added_channels = 0
        added_programmes = 0

        for channel in root.findall('channel'):
            channel_id = channel.get('id')
            if channel_id in target_channel_ids:
                new_root.append(channel)
                added_channels += 1
                print(f"✅ Found channel id: {channel_id}")

        for programme in root.findall('programme'):
            if programme.get('channel') in target_channel_ids:
                new_root.append(programme)
                added_programmes += 1

        tree_out = ET.ElementTree(new_root)
        tree_out.write(output_xml, encoding='utf-8', xml_declaration=True)
        print(f"\n✅ Filter complete. Added {added_channels} channels and {added_programmes} programmes.")
        print(f"💾 Output file created: {output_xml}")
    except Exception as e:
        print(f"❌ Error during filtering: {e}")
        exit(1)

# Step 5: Run full process
input_xml = "epg_source.xml"
output_xml = "filtered_epg.xml"

print("⬇️ Starting download and extraction...")
download_and_extract(epg_url, input_xml, input_xml + ".gz")

print(f"🔍 Filtering for channel IDs: {target_channel_ids}")
filter_epg_by_channel_id(input_xml, output_xml)
