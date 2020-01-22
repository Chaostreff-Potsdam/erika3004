import mimetypes

# Run from repository's main directory!
basePath = '../..F'

print("text")

file_path = basePath + 'tests/test_resources/test_ascii_art.txt'

mime = mimetypes.guess_type(file_path)
print(mime)
print()

print("BMP")
file_path = basePath + 'tests/test_resources/test_image_color.bmp'
mime = mimetypes.guess_type(file_path)
print(mime)
print()

print("PNG")
file_path = basePath + 'tests/test_resources/ubuntu-logo32.png'
mime = mimetypes.guess_type(file_path)
print(mime)
print()

#  FAIL
print("PNG - changed file extension to trick the library")
file_path = basePath + 'tests/test_resources/ubuntu-logo32.png.renamedwithextension.txt'
mime = mimetypes.guess_type(file_path)
print(mime)
print()
