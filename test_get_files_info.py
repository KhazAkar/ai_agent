from functions.get_files_info import get_files_info

print('get_files_info("calculator", "."):')
result = get_files_info("calculator", ".")
print("Result for current directory:")
if result.startswith("Error:"):
    print(f"  {result}")
else:
    for line in result.split("\n"):
        print(f"  {line}")

print()
print('get_files_info("calculator", "pkg"):')
result = get_files_info("calculator", "pkg")
print("Result for 'pkg' directory:")
if result.startswith("Error:"):
    print(f"  {result}")
else:
    for line in result.split("\n"):
        print(f"  {line}")

print()
print('get_files_info("calculator", "/bin"):')
result = get_files_info("calculator", "/bin")
print("Result for '/bin' directory:")
print(f"  {result}")

print()
print('get_files_info("calculator", "../"):')
result = get_files_info("calculator", "../")
print("Result for '../' directory:")
print(f"  {result}")
