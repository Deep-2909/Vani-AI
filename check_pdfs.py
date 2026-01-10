#!/usr/bin/env python3
"""
PDF Health Check Utility
Scans your data directory and identifies problematic PDFs
"""
import os
from pathlib import Path

def check_pdf_header(file_path: str) -> tuple:
    """
    Check if file has valid PDF header.
    Returns (is_valid, header_bytes, error_message)
    """
    try:
        with open(file_path, 'rb') as f:
            header = f.read(10)
            
            # Check for PDF header
            if header.startswith(b'%PDF'):
                return True, header, None
            else:
                return False, header, f"Invalid header: {header[:10]}"
    except Exception as e:
        return False, None, str(e)


def check_pdf_size(file_path: str) -> tuple:
    """
    Check file size.
    Returns (is_reasonable, size_bytes, warning)
    """
    try:
        size = os.path.getsize(file_path)
        
        if size == 0:
            return False, size, "File is empty"
        elif size < 1024:  # Less than 1KB
            return False, size, "File too small (likely corrupted)"
        else:
            return True, size, None
    except Exception as e:
        return False, 0, str(e)


def format_size(bytes_size: int) -> str:
    """Format bytes to human readable size"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"


def scan_data_directory(data_dir: str = "./data"):
    """
    Comprehensive scan of data directory.
    """
    print("=" * 80)
    print("🔍 PDF HEALTH CHECK UTILITY")
    print("=" * 80)
    
    if not os.path.exists(data_dir):
        print(f"\n❌ Directory '{data_dir}' not found!")
        print(f"💡 Creating directory: {data_dir}")
        os.makedirs(data_dir, exist_ok=True)
        print("✅ Directory created. Please add your PDF files.")
        return
    
    data_path = Path(data_dir)
    pdf_files = list(data_path.glob("**/*.pdf"))
    
    if not pdf_files:
        print(f"\n⚠️  No PDF files found in '{data_dir}'")
        print("💡 Add PDF documents to this directory and run again.")
        return
    
    print(f"\n📂 Found {len(pdf_files)} PDF files")
    print("=" * 80)
    
    # Categorize files
    valid_files = []
    corrupted_files = []
    suspicious_files = []
    
    for pdf_file in pdf_files:
        file_path = str(pdf_file)
        file_name = pdf_file.name
        
        # Check header
        is_valid_header, header, header_error = check_pdf_header(file_path)
        
        # Check size
        is_valid_size, size, size_warning = check_pdf_size(file_path)
        
        file_info = {
            'path': file_path,
            'name': file_name,
            'size': size,
            'header': header,
            'valid_header': is_valid_header,
            'valid_size': is_valid_size,
            'errors': []
        }
        
        if header_error:
            file_info['errors'].append(header_error)
        if size_warning:
            file_info['errors'].append(size_warning)
        
        # Categorize
        if is_valid_header and is_valid_size:
            valid_files.append(file_info)
        elif not is_valid_header or not is_valid_size:
            corrupted_files.append(file_info)
        else:
            suspicious_files.append(file_info)
    
    # Print results
    print("\n✅ VALID PDF FILES:")
    print("=" * 80)
    if valid_files:
        for file in valid_files:
            print(f"  ✓ {file['name']}")
            print(f"    Size: {format_size(file['size'])}")
            print()
    else:
        print("  (None found)")
    
    if corrupted_files:
        print("\n❌ CORRUPTED/INVALID FILES:")
        print("=" * 80)
        for file in corrupted_files:
            print(f"  ✗ {file['name']}")
            print(f"    Size: {format_size(file['size'])}")
            for error in file['errors']:
                print(f"    Issue: {error}")
            print()
    
    if suspicious_files:
        print("\n⚠️  SUSPICIOUS FILES:")
        print("=" * 80)
        for file in suspicious_files:
            print(f"  ⚠ {file['name']}")
            print(f"    Size: {format_size(file['size'])}")
            for error in file['errors']:
                print(f"    Warning: {error}")
            print()
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    print(f"  Total files: {len(pdf_files)}")
    print(f"  ✅ Valid: {len(valid_files)}")
    print(f"  ❌ Corrupted: {len(corrupted_files)}")
    print(f"  ⚠️  Suspicious: {len(suspicious_files)}")
    
    # Recommendations
    print("\n" + "=" * 80)
    print("💡 RECOMMENDATIONS")
    print("=" * 80)
    
    if corrupted_files:
        print("\n🔧 Fix corrupted files:")
        print("   1. Delete corrupted files from data directory")
        print("   2. Re-download from original source")
        print("   3. Or convert to PDF using online tools")
        print("\n   Files to fix:")
        for file in corrupted_files:
            print(f"      • {file['name']}")
    
    if valid_files:
        print(f"\n✅ Ready for ingestion: {len(valid_files)} files")
        print("   Run: python3 ingest_robust.py")
    
    # Generate cleanup script
    if corrupted_files:
        print("\n" + "=" * 80)
        print("🗑️  CLEANUP SCRIPT")
        print("=" * 80)
        print("\nTo remove corrupted files, run these commands:\n")
        for file in corrupted_files:
            print(f'rm "{file["path"]}"')
        print("\n⚠️  WARNING: This will permanently delete the files!")


def main():
    data_dir = "./data"
    scan_data_directory(data_dir)


if __name__ == "__main__":
    main()
