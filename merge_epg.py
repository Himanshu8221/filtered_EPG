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

# ✅ Step 2: Set target channel display-names (must match exactly)
target_channel_names = {
    "SONY SAB",
    "SONY SAB HD",
    "STAR Plus HD",
    "NAVSARJAN SANSKRUTI GUJARATI",
    # Add more exact names from <display-name> elements
}

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

# Step 4: Filter EPG XML based on display-name
def filter_epg_by_display_name(input_xml, output_xml):
    try:
        print(f"📂 Parsing EPG file: {input_xml}")
        tree = ET.parse(input_xml)
        root = tree.getroot()

        new_root = ET.Element('tv')
        matched_channel_ids = set()
        added_channels = 0
        added_programmes = 0

        print("\n📋 Available channel names:")
        for channel in root.findall('channel'):
            for display_name in channel.findall('display-name'):
                if display_name.text:
                    name = display_name.text.strip()
                    print("-", name)
                    if name in target_channel_names:
                        channel_id = channel.get('id')
                        matched_channel_ids.add(channel_id)
                        new_root.append(channel)
                        added_channels += 1
                        break

        for programme in root.findall('programme'):
            if programme.get('channel') in matched_channel_ids:
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

print(f"🔍 Filtering for: {target_channel_names}")
filter_epg_by_display_name(input_xml, output_xml)
