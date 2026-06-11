"""
One-time migration script: creates sections from existing offering data.
Reads all distinct section strings from class_offerings, inserts them
into a new sections collection, sets section_id on each offering,
and removes the old free-text section field.

Usage:
    source venv/bin/activate && python migrate_sections.py
"""

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

MONGO_URI = "mongodb://localhost:27017/student-management-record"


def main():
    client = MongoClient(MONGO_URI)
    db = client.get_default_database()

    print("Checking existing sections collection...")
    existing = db.sections.count_documents({})
    if existing > 0:
        print(f"  Sections collection already has {existing} entries. Skipping seed.")
    else:
        print("  Gathering unique section names from class_offerings...")
        distinct = db.class_offerings.distinct("section")
        distinct = [s for s in distinct if s]
        print(f"  Found {len(distinct)} unique section(s): {', '.join(distinct)}")

        # Get current max counter
        counter = db.counters.find_one({"_id": "sections"})
        next_id = (counter["seq"] + 1) if counter else 1

        section_map = {}
        for name in sorted(distinct):
            sid = next_id
            next_id += 1
            try:
                db.sections.insert_one({"_id": sid, "name": name})
                section_map[name] = sid
                print(f"    Created section '{name}' with id={sid}")
            except DuplicateKeyError:
                existing_doc = db.sections.find_one({"name": name})
                if existing_doc:
                    section_map[name] = existing_doc["_id"]

        # Update counters
        db.counters.update_one(
            {"_id": "sections"},
            {"$set": {"seq": next_id - 1}},
            upsert=True
        )

    # Get all sections (in case some already existed)
    all_sections = {s["name"]: s["_id"] for s in db.sections.find()}

    print("\nUpdating class_offerings to use section_id...")
    updated = 0
    for offering in db.class_offerings.find({"section": {"$exists": True}}):
        section_name = offering.get("section", "")
        if not section_name:
            continue
        section_id = all_sections.get(section_name)
        if section_id is None:
            print(f"  WARNING: No section found for '{section_name}' (offering {offering['_id']})")
            continue
        db.class_offerings.update_one(
            {"_id": offering["_id"]},
            {"$set": {"section_id": section_id}, "$unset": {"section": ""}}
        )
        updated += 1

    # Also handle offerings that might already have section_id but still have old section field
    for offering in db.class_offerings.find({"section_id": {"$exists": True}, "section": {"$exists": True}}):
        db.class_offerings.update_one(
            {"_id": offering["_id"]},
            {"$unset": {"section": ""}}
        )

    print(f"  Updated {updated} offering(s)")
    print("\nMigration complete!")
    print(f"  Sections: {db.sections.count_documents({})}")
    print(f"  Offerings with section_id: {db.class_offerings.count_documents({'section_id': {'$exists': True}})}")


if __name__ == "__main__":
    main()
