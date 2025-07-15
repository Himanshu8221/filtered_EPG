import os
import xml.etree.ElementTree as ET
import requests
import gzip
import shutil

print("🔧 Starting EPG filter process...")

# Step 1: Read environment variable
epg_url = os.getenv("EPG_URL_1")

print("📥 Checking environment variable...")
if not epg_url:
    print("❌ EPG_URL_1 is missing.")
    exit(1)

# Step 2: Define selected channel IDs
selected_channel_ids = {
    "61", "52", "8", "51",
}

# Step 3: Download and extract EPG
def download_and_extract(url, out_xml, temp_gz):
    try:
        print(f"➡️ Downloading from: {url}")
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        with open(temp_gz, 'wb') as f:
            f.write(r.content)
        print(f"✅ Downloaded: {temp_gz}")
        
        # Decompress
        with gzip.open(temp_gz, 'rb') as f_in:
            with open(out_xml, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        print(f"📂 Extracted to: {out_xml}")
    except Exception as e:
        print(f"❌ Failed to download or extract {url}: {e}")
        exit(1)

# Step 4: Filter selected channels and programmes
def filter_epg(input_xml, output_xml):
    try:
        print(f"📂 Parsing EPG file: {input_xml}")
        tree = ET.parse(input_xml)
        root = tree.getroot()

        new_root = ET.Element('tv')

        added_channels = 0
        added_programmes = 0

        for channel in root.findall('channel'):
            channel_id = channel.get('id')
            if channel_id in selected_channel_ids:
                new_root.append(channel)
                added_channels += 1

        for programme in root.findall('programme'):
            programme_channel = programme.get('channel')
            if programme_channel in selected_channel_ids:
                new_root.append(programme)
                added_programmes += 1

        tree_out = ET.ElementTree(new_root)
        tree_out.write(output_xml, encoding='utf-8', xml_declaration=True)
        print(f"✅ Filter complete. Added {added_channels} channels and {added_programmes} programmes.")
        print(f"💾 Filtered EPG saved as: {output_xml}")
    except Exception as e:
        print(f"❌ Error during filtering: {e}")
        exit(1)

# Step 5: Run the process
print("⬇️ Starting download and extraction...")
download_and_extract(epg_url, 'epg_source.xml', 'epg_source.xml.gz')

print("🔍 Filtering selected channel IDs...")
filter_epg('epg_source.xml', 'filtered_epg.xml')
