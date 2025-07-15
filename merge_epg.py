import os
import xml.etree.ElementTree as ET
import requests
import gzip
import shutil

print("🔧 Starting EPG filter process...")

epg_url = os.getenv("EPG_URL_1")

if not epg_url:
    print("❌ EPG_URL_1 is missing.")
    exit(1)

# Make sure to use string channel IDs
target_channel_ids = {"8", "51", "61", "52", "123", "245", "616" }

def download_and_extract(url, out_xml, temp_gz):
    try:
        print(f"➡️ Downloading from: {url}")
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        with open(temp_gz, 'wb') as f:
            f.write(r.content)
        print(f"✅ Downloaded: {temp_gz}")

        with gzip.open(temp_gz, 'rb') as f_in:
            with open(out_xml, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        print(f"📂 Extracted to: {out_xml}")
    except Exception as e:
        print(f"❌ Failed to download or extract: {e}")
        exit(1)

def filter_epg(input_xml, output_xml):
    try:
        tree = ET.parse(input_xml)
        root = tree.getroot()

        # Root element should be <tv>
        new_root = ET.Element("tv")
        added_channels = 0
        added_programmes = 0

        print("\n🔍 Looking for matching channels...")
        for channel in root.findall(".//channel"):
            cid = channel.get("id")
            if cid in target_channel_ids:
                new_root.append(channel)
                added_channels += 1
                print(f"✅ Matched channel id={cid}")

        print("\n🔍 Looking for matching programmes...")
        for programme in root.findall(".//programme"):
            if programme.get("channel") in target_channel_ids:
                new_root.append(programme)
                added_programmes += 1

        print(f"\n✅ Added {added_channels} channels and {added_programmes} programmes.")

        # Write output XML
        ET.ElementTree(new_root).write(output_xml, encoding="utf-8", xml_declaration=True)
        print(f"💾 Output saved: {output_xml}")

    except Exception as e:
        print(f"❌ Error while filtering: {e}")
        exit(1)

# Run the process
input_xml = "epg_source.xml"
output_xml = "filtered_epg.xml"

download_and_extract(epg_url, input_xml, input_xml + ".gz")
filter_epg(input_xml, output_xml)
