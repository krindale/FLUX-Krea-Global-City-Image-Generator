#!/usr/bin/env python3
"""
이미지 최적화 스크립트
1024x1024 크기를 유지하면서 파일 용량을 줄입니다.
"""

import os
import sys
from PIL import Image
from pathlib import Path
import argparse

def optimize_image(input_path, output_path=None, quality=85, optimize=True):
    """
    이미지를 최적화하여 용량을 줄입니다.
    
    Args:
        input_path: 입력 이미지 경로
        output_path: 출력 이미지 경로 (None이면 원본 덮어쓰기)
        quality: JPEG 품질 (1-100, PNG의 경우 무시됨)
        optimize: 최적화 옵션 사용 여부
    """
    try:
        with Image.open(input_path) as img:
            # 이미지 크기 확인
            print(f"Processing: {input_path}")
            print(f"Original size: {img.size}")
            
            # 1024x1024가 아니면 리사이즈
            if img.size != (1024, 1024):
                img = img.resize((1024, 1024), Image.Resampling.LANCZOS)
                print(f"Resized to: {img.size}")
            
            # 출력 경로 설정
            if output_path is None:
                output_path = input_path
            
            # 원본 파일 크기
            original_size = os.path.getsize(input_path)
            
            # 파일 확장자에 따른 최적화
            file_ext = Path(input_path).suffix.lower()
            
            if file_ext in ['.jpg', '.jpeg']:
                # JPEG 최적화
                img.save(output_path, 'JPEG', quality=quality, optimize=optimize)
            elif file_ext == '.png':
                # PNG 최적화 - 색상 수 줄이기 시도
                if img.mode in ('RGBA', 'LA'):
                    # 알파 채널이 있는 경우
                    img.save(output_path, 'PNG', optimize=optimize)
                else:
                    # 알파 채널이 없는 경우 색상 수 줄이기 시도
                    try:
                        # P 모드로 변환하여 팔레트 압축 시도
                        img_p = img.convert('P', palette=Image.ADAPTIVE, colors=256)
                        img_p.save(output_path, 'PNG', optimize=optimize)
                    except:
                        # 실패하면 원본 모드로 저장
                        img.save(output_path, 'PNG', optimize=optimize)
            else:
                # 기타 형식
                img.save(output_path, optimize=optimize)
            
            # 결과 출력
            new_size = os.path.getsize(output_path)
            reduction = (1 - new_size/original_size) * 100
            
            print(f"Original: {original_size:,} bytes")
            print(f"Optimized: {new_size:,} bytes")
            print(f"Reduction: {reduction:.1f}%")
            print("-" * 50)
            
            return True
            
    except Exception as e:
        print(f"Error processing {input_path}: {e}")
        return False

def optimize_folder(folder_path, quality=85, backup=True, recursive=True):
    """
    폴더 내 모든 이미지를 최적화합니다.
    
    Args:
        folder_path: 폴더 경로
        quality: JPEG 품질
        backup: 백업 생성 여부
        recursive: 하위 폴더까지 재귀 탐색 여부
    """
    folder = Path(folder_path)
    if not folder.exists():
        print(f"폴더가 존재하지 않습니다: {folder_path}")
        return
    
    # 지원되는 이미지 확장자
    image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp'}
    
    # 이미지 파일 찾기 (재귀적 또는 단일 폴더)
    image_files = []
    if recursive:
        # 하위 폴더까지 모든 이미지 파일 찾기
        for ext in image_extensions:
            image_files.extend(folder.rglob(f'*{ext}'))  # rglob for recursive
            image_files.extend(folder.rglob(f'*{ext.upper()}'))
    else:
        # 현재 폴더만 검색
        for ext in image_extensions:
            image_files.extend(folder.glob(f'*{ext}'))
            image_files.extend(folder.glob(f'*{ext.upper()}'))
    
    # backup 폴더는 제외
    image_files = [f for f in image_files if 'backup' not in f.parts]
    
    if not image_files:
        print("최적화할 이미지 파일이 없습니다.")
        return
    
    print(f"발견된 이미지 파일: {len(image_files)}개")
    
    # 폴더별로 그룹화하여 표시
    folders = {}
    for img_file in image_files:
        folder_name = str(img_file.parent.relative_to(folder))
        if folder_name == '.':
            folder_name = '(root)'
        if folder_name not in folders:
            folders[folder_name] = []
        folders[folder_name].append(img_file.name)
    
    print("\n[Folders] Image files by directory:")
    for folder_name, files in folders.items():
        print(f"   {folder_name}: {len(files)} files")
        for file in files[:3]:  # 처음 3개만 표시
            print(f"      - {file}")
        if len(files) > 3:
            print(f"      ... and {len(files)-3} more")
    print("=" * 50)
    
    # 백업 폴더 생성
    if backup:
        backup_folder = folder / 'backup'
        backup_folder.mkdir(exist_ok=True)
        print(f"백업 폴더: {backup_folder}")
    
    total_original = 0
    total_optimized = 0
    success_count = 0
    
    for img_file in image_files:
        try:
            # 백업 생성 (상대 경로 유지)
            if backup:
                # 원본 파일의 상대 경로를 유지하여 백업
                relative_path = img_file.relative_to(folder)
                backup_path = backup_folder / relative_path
                
                # 백업 폴더 구조 생성
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                
                if not backup_path.exists():
                    import shutil
                    shutil.copy2(img_file, backup_path)
            
            # 원본 크기 기록
            original_size = img_file.stat().st_size
            total_original += original_size
            
            # 최적화 실행
            if optimize_image(str(img_file), quality=quality):
                success_count += 1
                new_size = img_file.stat().st_size
                total_optimized += new_size
            
        except Exception as e:
            print(f"Error with {img_file}: {e}")
    
    # 전체 결과 요약
    print("=" * 50)
    print("최적화 완료!")
    print(f"처리된 파일: {success_count}/{len(image_files)}")
    print(f"전체 원본 크기: {total_original:,} bytes ({total_original/1024/1024:.1f} MB)")
    print(f"전체 최적화 크기: {total_optimized:,} bytes ({total_optimized/1024/1024:.1f} MB)")
    if total_original > 0:
        total_reduction = (1 - total_optimized/total_original) * 100
        print(f"전체 용량 절약: {total_reduction:.1f}% ({(total_original-total_optimized)/1024/1024:.1f} MB)")

def main():
    parser = argparse.ArgumentParser(description='이미지 최적화 도구')
    parser.add_argument('path', help='이미지 파일 또는 폴더 경로')
    parser.add_argument('--quality', type=int, default=85, help='JPEG 품질 (1-100, 기본값: 85)')
    parser.add_argument('--no-backup', action='store_true', help='백업 생성하지 않음')
    parser.add_argument('--output', help='출력 경로 (단일 파일 처리시)')
    parser.add_argument('--no-recursive', action='store_true', help='하위 폴더 탐색 안함')
    
    args = parser.parse_args()
    
    path = Path(args.path)
    
    if not path.exists():
        print(f"경로가 존재하지 않습니다: {args.path}")
        sys.exit(1)
    
    if path.is_file():
        # 단일 파일 처리
        print("단일 파일 최적화")
        print("=" * 50)
        optimize_image(str(path), args.output, args.quality)
    elif path.is_dir():
        # 폴더 처리
        print(f"폴더 최적화: {path}")
        print("=" * 50)
        optimize_folder(str(path), args.quality, not args.no_backup, recursive=not args.no_recursive)
    else:
        print("유효하지 않은 경로입니다.")
        sys.exit(1)

if __name__ == '__main__':
    main()