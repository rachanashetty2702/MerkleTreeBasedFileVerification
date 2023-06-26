import os
import hashlib
import pickle
import time
import subprocess

class MerkleTree:
    def __init__(self):
        self.root = None

    def build_tree(self, files):
        files.sort()  # Sort the files alphabetically
        if len(files) == 0:
            return None
        if len(files) == 1:
            return MerkleNode(data=self.read_file(files[0]), file_name=files[0])

        mid = len(files) // 2
        left_child = self.build_tree(files[:mid])
        right_child = self.build_tree(files[mid:])
        return MerkleNode(left_child=left_child, right_child=right_child)

    def generate_hash(self, data):
        hash_object = hashlib.sha256()
        hash_object.update(data.encode())
        return hash_object.hexdigest()

    def update_node_hash(self, node):
        if node.left_child is None and node.right_child is None:
            node.hash_value = self.generate_hash(node.data)
        else:
            self.update_node_hash(node.left_child)
            self.update_node_hash(node.right_child)
            if node.left_child is not None and node.right_child is not None:
                node.hash_value = self.generate_hash(node.left_child.hash_value + node.right_child.hash_value)

    def verify_tree(self, node, changes):
        if node.left_child is None and node.right_child is None:
            if node.hash_value != node.calculated_hash:
                changes.append((node.file_name, "Modified", time.ctime()))
            else:
                changes.append((node.file_name, "No Changes", node.hash_value))
        else:
            self.verify_tree(node.left_child, changes)
            self.verify_tree(node.right_child, changes)

    def update_tree(self, node, file_name):
        if node.left_child is None and node.right_child is None:
            if node.file_name == file_name:
                node.data = self.read_file(file_name)
                node.calculated_hash = self.generate_hash(node.data)
        else:
            if node.left_child is not None:
                self.update_tree(node.left_child, file_name)
            if node.right_child is not None:
                self.update_tree(node.right_child, file_name)
            if node.left_child is not None and node.right_child is not None:
                node.hash_value = self.generate_hash(node.left_child.hash_value + node.right_child.hash_value)

    def read_file(self, file_name):
        with open(file_name, "r") as file:
            data = file.read()
        return data


class MerkleNode:
    def __init__(self, left_child=None, right_child=None, data=None, file_name=None):
        self.left_child = left_child
        self.right_child = right_child
        self.data = data
        self.file_name = file_name
        self.calculated_hash = None
        self.hash_value = None


def save_merkle_tree(root):
    with open("merkle_tree.pkl", "wb") as file:
        pickle.dump(root, file)


def load_merkle_tree():
    if not os.path.exists("merkle_tree.pkl"):
        return None
    with open("merkle_tree.pkl", "rb") as file:
        return pickle.load(file)


def display_menu():
    print("Merkle Tree File Verification System")
    print("====================================")
    print("1. Add a file to the directory")
    print("2. Delete a file from the directory")
    print("3. Rename a file")
    print("4. Modify the data in a file")
    print("5. Check if any file data has been modified")
    print("6. Search for a file")
    print("7. Display file changes")
    print("8. Exit")
    print("====================================")


def add_file(directory):
    file_name = input("Enter the name of the file: ")
    file_path = os.path.join(directory, file_name)
    if os.path.exists(file_path):
        print("File already exists!\n")
        return
    with open(file_path, "w") as file:
        pass
    print(f"File '{file_name}' added successfully!\n")

    # Sort files in the directory alphabetically
    files = [file for file in os.listdir(directory) if os.path.isfile(os.path.join(directory, file))]
    files.sort()
    for file in files:
        print(file)
    print("====================================")


def delete_file(directory):
    file_name = input("Enter the name of the file to delete: ")
    file_path = os.path.join(directory, file_name)
    if not os.path.exists(file_path):
        print("File does not exist!\n")
        return
    os.remove(file_path)
    print(f"File '{file_name}' deleted successfully!\n")


def rename_file(directory):
    old_file_name = input("Enter the name of the file to rename: ")
    new_file_name = input("Enter the new name for the file: ")
    old_file_path = os.path.join(directory, old_file_name)
    new_file_path = os.path.join(directory, new_file_name)
    if not os.path.exists(old_file_path):
        print("File does not exist!\n")
        return
    os.rename(old_file_path, new_file_path)
    print(f"File '{old_file_name}' renamed to '{new_file_name}' successfully!\n")


def modify_file(directory):
    file_name = input("Enter the name of the file to modify: ")
    file_path = os.path.join(directory, file_name)
    if not os.path.exists(file_path):
        print("File does not exist!\n")
        return
    with open(file_path, "w") as file:
        new_data = input("Enter the new data for the file: ")
        file.write(new_data)
    print(f"File '{file_name}' modified successfully!\n")

def search_file(directory):
    file_name = input("Enter the name of the file to search: ")
    file_path = os.path.join(directory, file_name)
    if os.path.exists(file_path):
        print(f"File '{file_name}' found!\n")
    else:
        print(f"File '{file_name}' not found!\n")


def check_file_changes(directory, merkle_tree):
    changes = []
    merkle_tree.verify_tree(merkle_tree.root, changes)
    print("All files in the directory:")
    files = [file for file in os.listdir(directory) if os.path.isfile(os.path.join(directory, file))]
    for file in files:
        print(file)

    print("====================================")
    option = input("Enter 'y' to see the detailed changes or else press 'n' to continue: ")
    if option.lower() == 'y':
        subprocess.call(['python', 'merkle.py'])


def main():
    directory = input("Enter the directory path: ")
    if not os.path.exists(directory):
        print("Directory does not exist!")
        return

    merkle_tree = MerkleTree()
    merkle_tree.root = load_merkle_tree()
    if merkle_tree.root is None:
        files = [os.path.join(directory, file) for file in os.listdir(directory) if
                 os.path.isfile(os.path.join(directory, file))]
        files.sort()  # Sort files in alphabetical order
        merkle_tree.root = merkle_tree.build_tree(files)
        merkle_tree.update_node_hash(merkle_tree.root)
        save_merkle_tree(merkle_tree.root)

    while True:
        display_menu()
        choice = input("Enter your choice (1-6): ")
        print("====================================")
        if choice == "1":
            add_file(directory)
            merkle_tree.update_tree(merkle_tree.root, file_name="")
            merkle_tree.update_node_hash(merkle_tree.root)
            save_merkle_tree(merkle_tree.root)
        elif choice == "2":
            delete_file(directory)
            merkle_tree.update_tree(merkle_tree.root, file_name="")
            merkle_tree.update_node_hash(merkle_tree.root)
            save_merkle_tree(merkle_tree.root)
        elif choice == "3":
            rename_file(directory)
            merkle_tree.update_tree(merkle_tree.root, file_name="")
            merkle_tree.update_node_hash(merkle_tree.root)
            save_merkle_tree(merkle_tree.root)
        elif choice == "4":
            modify_file(directory)
            merkle_tree.update_tree(merkle_tree.root, file_name="")
            merkle_tree.update_node_hash(merkle_tree.root)
            save_merkle_tree(merkle_tree.root)
        elif choice == "5":
            check_file_changes(directory, merkle_tree)
        elif choice == "6":
            search_file(directory)
        elif choice == "7":
            subprocess.call(['python', 'm.py'])
        elif choice == "8":
            print("Exiting...")
            break
        else:
            print("Invalid choice! Please enter a number from 1 to 6.\n")


if __name__ == "__main__":
    main()

