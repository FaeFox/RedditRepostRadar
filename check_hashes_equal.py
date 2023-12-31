from PIL import Image
import imagehash
# This is the reverse script that effectively checks for reposts given two hashes. This is just a test for now.


def are_hashes_similar(hash_str1, hash_str2, cutoff):
    # Converts to hash
    hash1 = imagehash.hex_to_hash(hash_str1)
    hash2 = imagehash.hex_to_hash(hash_str2)

    # Confronta gli oggetti hash considerando il cutoff
    return hash1 - hash2 < cutoff


# Compare two hashes from the JSON file
hash_str1 = "0808d496174f8fff"
hash_str2 = "080cd496170f0fff"
cutoff_value = 5

if are_hashes_similar(hash_str1, hash_str2, cutoff_value):
    print("Images are similar")
else:
    print("Images are not similar")