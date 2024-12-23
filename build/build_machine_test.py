import os
import subprocess
import shutil
from datetime import datetime

def force_remove_dir(directory):
    def onerror(func, path, exc_info):
        os.chmod(path, 0o777)  # 권한 수정
        func(path)  # 삭제 재시도

    if os.path.exists(directory):
        shutil.rmtree(directory, onerror=onerror)
        
def git_clone(repo_url, clone_dir, log_dir, branch_name=None):
    
    if os.path.exists(clone_dir):
        print(f"Directory {clone_dir} already exists. Deleting its contents...")
        force_remove_dir(clone_dir)
        print(f"Directory {clone_dir} has been cleared.")
        
    # os.makedirs(clone_dir, exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)
    
    log_file_path = os.path.join(log_dir, f"git_clone_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    
    try:
        print(f"Cloning repository: {repo_url}")
        
        git_command = ["git", "clone"]
        if branch_name:
            git_command += ["-b", branch_name]
        git_command += [repo_url, clone_dir]
        
        with open(log_file_path, 'w') as log_file:
            result = subprocess.run(
                git_command,
                stdout=log_file,
                stderr=log_file,
                text=True
            )
        
        if result.returncode != 0:
            print(f"Git clone failed. Check log: {log_file_path}")
        else:
            print(f"Repository cloned to: {clone_dir}")
    
    except Exception as e:
        print(f"Error during git clone: {e}")

def build_solution(solution_path, build_output_dir, log_dir, msbuild_path):
    if not os.path.exists(solution_path):
        raise FileNotFoundError(f"Solution file not found: {solution_path}")
    
    os.makedirs(build_output_dir, exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)
    
    log_file_path = os.path.join(log_dir, f"build_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    
    build_command = [
        msbuild_path,
        solution_path,
        "/p:Configuration=Release",
        "/p:Platform=x64",
        f"/fileLoggerParameters:LogFile={log_file_path}",
    ]
    
    try:
        print(f"Building solution: {solution_path}")
        result = subprocess.run(build_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode != 0:
            print(f"Build failed. Check log: {log_file_path}")
            with open(log_file_path, 'a') as log_file:
                log_file.write(result.stderr)
            return
        
        print("Build succeeded.")
        output_exe_path = os.path.join(os.path.dirname(solution_path), "x64", "Release")
        if os.path.exists(output_exe_path):
            for file in os.listdir(output_exe_path):
                shutil.copy(os.path.join(output_exe_path, file), build_output_dir)
            print(f"Build output copied to: {build_output_dir}")
        else:
            print(f"No output found at: {output_exe_path}")
    
    except Exception as e:
        print(f"Error during build: {e}")

if __name__ == "__main__":
    repo_url = "https://github.com/cagongman/L-SCAN_buildMachine.git"  # 클론할 Git 저장소 URL
    clone_dir = r"..\build_result\GitClone"  # 클론 디렉토리
    build_output_dir = r"..\build_result\Build"  # 빌드 결과물 저장 경로
    log_dir = r"..\build_result\Log"  # 로그 파일 저장 경로
    branch_name = "develop"
    msbuild_path = r"C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\MSBuild\Current\Bin\MSBuild.exe"
    solution_name = "test_build.sln"  # 솔루션 파일 이름

    git_clone(repo_url, clone_dir, log_dir, branch_name)
    
    solution_path = os.path.join(clone_dir, r"VS_WS\test_build", solution_name)
    build_solution(solution_path, build_output_dir, log_dir, msbuild_path)
