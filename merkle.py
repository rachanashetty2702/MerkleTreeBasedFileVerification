import hashlib
import os

class MerkleTreeNode:
    def __init__(self, value, data):
        self.left = None
        self.right = None
        self.value = value
        self.hashValue = hashlib.sha256(value.encode('utf-8')).hexdigest()
        self.data = data

    def verify_tree(self, node, changes):
        if node is None:
            return

        if node.left is None and node.right is None:
            # Leaf node
            if node.value not in changes:
                changes.append(node.value)
        else:
            # Internal node
            self.verify_tree(node.left, changes)
            self.verify_tree(node.right, changes)

def hash_file(file_path):
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    file_hash = hasher.hexdigest()

    with open(file_path, 'r') as f:
        file_content = f.read()

    return file_hash, file_content

def build_tree(directory_path, f):
    nodes = []
    for root, _, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_hash, file_content = hash_file(file_path)
            nodes.append(MerkleTreeNode(file_hash, file_content))
            if f:
                f.write("File: " + file_path + " | Hash: " + file_hash + "\n")

    while len(nodes) != 1:
        temp = []
        for i in range(0, len(nodes), 2):
            node1 = nodes[i]
            if i + 1 < len(nodes):
                node2 = nodes[i + 1]
            else:
                temp.append(nodes[i])
                break
            concatenated_hash = node1.hashValue + node2.hashValue
            parent = MerkleTreeNode(concatenated_hash, "")
            parent.left = node1
            parent.right = node2
            temp.append(parent)
        nodes = temp
    return nodes[0]

def compare_hashes(directory_path):
    old_hashes = {}
    if os.path.exists("merkle.tree"):
        with open("merkle.tree", "r") as f:
            for line in f:
                if line.startswith("File:"):
                    file_path, file_hash = line.strip().split("|")
                    file_path = file_path.split(":", 1)[1].strip()
                    file_hash = file_hash.split(":", 1)[1].strip()
                    old_hashes[file_path] = file_hash

    new_root_hash = build_tree(directory_path, None).hashValue
    modified_files = []

    if old_hashes:
        for file_path, file_hash in old_hashes.items():
            if os.path.exists(file_path):
                new_hash, _ = hash_file(file_path)
                if file_hash != new_hash:
                    print("Changes detected in file:", file_path)
                    print("Old Hash:", file_hash)
                    print("New Hash:", new_hash)
                    modified_files.append(file_path)
                    compare_file_changes(file_path)
            else:
                print("File removed:", file_path)

        if modified_files:
            print("Changes detected in the Merkle tree\n")
        else:
            print("No changes detected in the Merkle tree\n")
    else:
        print("No previous Merkle tree found")

    with open("merkle.tree", "w") as f:
        for root, _, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_hash, _ = hash_file(file_path)
                f.write("File: " + file_path + " | Hash: " + file_hash + "\n")

    return modified_files

def compare_file_changes(file_path):
    with open(file_path, "r") as f:
        old_contents = f.read()

    with open(file_path, "r") as f:
        new_contents = f.read()

    if old_contents != new_contents:
        print("Changes made to file:", file_path)
        print("Old Contents:")
        print(old_contents)
        print("New Contents:")
        print(new_contents)

def check_file_changes(directory):
    changes = []
    modified_files = compare_hashes(directory)
    merkle_tree = build_tree(directory, None)
    merkle_tree.verify_tree(merkle_tree, changes)
    files = [file for file in os.listdir(directory) if os.path.isfile(os.path.join(directory, file))]

if __name__ == "__main__":
    directory_path = r"C:\Users\rachana\OneDrive\Desktop\HashTree"
    check_file_changes(directory_path)
