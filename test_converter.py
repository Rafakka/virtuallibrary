from converter import BookConverter

converter = BookConverter('/home/kai/Git/virtuallibrary')
pdf_path = converter.convert_epub_to_pdf('/home/kai/Git/virtuallibrary/bundle test/zlib.pub_the-tao-of-immortality-the-four-healing-arts-and-the-nine-levels-of-alchemy.epub')
print(f"✅ Converted to: {pdf_path}")