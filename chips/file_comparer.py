import os

def compare_files(file_1_name, file_2_name):
    script_dir = os.path.dirname(__file__)
    file_1_path = os.path.join(script_dir, (file_1_name + ".hack"))
    file_2_path = os.path.join(script_dir, (file_2_name + ".hack"))

    file_1_lines = []
    file_2_lines = []

    with open(file_1_path, "r") as file_1:
        for line in file_1:
            file_1_lines.append(line.strip())
        
    with open(file_2_path, "r") as file_2:
        for line in file_2:
            file_2_lines.append(line.strip())
    if file_1_lines == file_2_lines:
        return True
    return False



if __name__ == "__main__":
    file_1_name = "test"
    file_2_name = "chat_test"
    print(f"{file_1_name} has the same contents as {file_2_name}: {compare_files(file_1_name, file_2_name)}")