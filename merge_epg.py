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

# ✅ Step 2: Use display-names to filter
selected_channel_names = {
    "Sony SAB HD",
    "Star Plus HD",
    "Zee TV HD",
    "Colors HD",
    # Add more display-names exactly as they appear in the XML
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

# Step 4: Filter by <display-name>
def filter_epg_by_display_name(input_xml, output_xml):
    try:
        print(f"📂 Parsing EPG file: {input_xml}")
        tree = ET.parse(input_xml)
        root = tree.getroot()

        new_root = ET.Element('tv')
        selected_ids = set()
        added_channels = 0
        added_programmes = 0

        # Find channels with matching display-name
        for channel in root.findall('channel'):
            for dn in channel.findall('display-name'):
                if dn.text and dn.text.strip() in selected_channel_names:
                    selected_ids.add(channel.get('id'))
                    new_root.append(channel)
                    added_channels += 1
                    break

        # Copy only <programme> for selected channel ids
        for programme in root.findall('programme'):
            if programme.get('channel') in selected_ids:
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

print("🔍 Filtering by channel name...")
filter_epg_by_display_name('epg_source.xml', 'filtered_epg.xml')
