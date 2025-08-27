#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
本脚本用于遍历 root_dir 下所有子目录，
尝试使用 dpdata 读取 DeepMD (npy) 格式的数据，并转换为 ASE 的 Atoms 对象。
在每个子目录下生成一个 extxyz 文件（output.extxyz），
并将所有帧合并到 root_dir 目录下的 total_mace.xyz 文件中。
"""

import os
import dpdata as dp
from dpdata.plugins.ase import ASEStructureFormat
from ase.io import write

# ======================== 变量定义区 ========================
# 根目录：脚本会递归搜索此目录及其所有子目录
root_dir = "./"

# 原子类型映射：如果 type.raw 或 npy 中是整型 (0,1,2,3)，
# 则需要在此列表中按顺序指定对应的元素符号。
my_type_map = ["Li", "Ge", "P", "S"]

# 每个子目录写出的 extxyz 文件名
per_dir_extxyz_name = "output.extxyz"

# 合并后在根目录下写出的 extxyz 文件名
merged_extxyz_name = "total_mace.xyz"
# ======================== 变量定义区 ========================

# 用于累积所有转换得到的 Atoms 帧
all_atoms = []

# 遍历 root_dir 及所有子目录
for dirpath, dirnames, filenames in os.walk(root_dir):
    try:
        # 1) 尝试将当前目录作为 deepmd label 数据读取 (npy 格式)
        # 如果目录里混合 npy 和 raw，可以改用 fmt="deepmd/npy/mixed"
        ls = dp.LabeledSystem(dirpath, fmt="deepmd/npy", type_map=my_type_map)
        
        # 2) 转换为 ASE 的 Atoms 对象列表
        atoms_list = ASEStructureFormat().to_system(ls.data)
        
        # 3) 如果有能量、力和 virial，则手动添加到 Atoms 对象
        energies = ls.data.get("energies", None)
        forces = ls.data.get("forces", None)
        virials = ls.data.get("virials", None)  # 有些版本可能键名为 "virial"
        
        if energies is not None:
            for i, atoms in enumerate(atoms_list):
                atoms.info["energy"] = float(energies[i])
        if forces is not None:
            for i, atoms in enumerate(atoms_list):
                atoms.arrays["forces"] = forces[i]
        if virials is not None:
            for i, atoms in enumerate(atoms_list):
                atoms.info["virial"] = virials[i]
        
        # 4) 统计帧数，写出单目录的 extxyz 文件
        num_frames = len(atoms_list)
        output_path = os.path.join(dirpath, per_dir_extxyz_name)
        
        print(f"正在转换目录: {dirpath}")
        print(f"该目录转换的 LabeledSystem 帧数: {num_frames}")
        print(f"输出文件将保存至: {output_path}")
        
        write(output_path, atoms_list, format="extxyz")
        print(f"目录 {dirpath} 转换完成。\n")
        
        # 5) 将该目录所有帧累积到全局列表中
        all_atoms.extend(atoms_list)
        
    except Exception as e:
        # 如果该目录不能作为合法的 deepmd label 数据读取，则跳过
        print(f"跳过目录 {dirpath}: {e}")
        continue

# 6) 合并所有帧并写出到根目录下的 total_mace.xyz 文件
merged_file = os.path.join(root_dir, merged_extxyz_name)
write(merged_file, all_atoms, format="extxyz")

print(f"\n合并完成，共 {len(all_atoms)} 帧数据，写出到 {merged_file}")
