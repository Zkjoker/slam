# coding=UTF-8
import argparse
import os
import sys
import subprocess
import signal

docker_cmd = "docker run --env=\"DISPLAY\" " \
                "--net=host " \
                "--volume=\"$HOME/.Xauthority:/root/.Xauthority:rw\" " \
                 "--env=\"QT_X11_NO_MITSHM=1\"" \
                " -v /tmp/.X11-unix:/tmp/.X11-unix:ro -it --rm --name slam_from_qt " \
                "-v /home:/out_home {} " \
                " /bin/bash -c \" cd root && /bin/bash /root/run_{}.sh {}\""


# "vins_mono", "svo", "vins_mono", "svo",
slam_types = ["全部", "基于滤波器", "特征法", "直接法", "多传感器融合","RGBD-传感器","激光雷达传感器"]
type2algos = {"全部": ["vins_mono", "dso", "svo", "okvis", "orb_slam", "lsd_slam", "rovio", "basalt", "ice_ba", "msckf","dvo","rgbdslam","gmapping","hector_slam","cartographer"],
              "基于滤波器": ["msckf","rovio"],
              "特征法": ["orb_slam","okvis","vins_mono","basalt"],
              "直接法": ["lsd_slam", "dso"],
              "多传感器融合": ["vins_mono", "svo", "okvis", "rovio", "basalt", "ice_ba", "msckf"],
              "RGB-D传感器":["dvo","rgbdslam"],
              "激光雷达传感器":["gmapping","hector_slam","cartographer"]}

algo2image = {algo:"zkjoker/image1:19-12-30" for algo in ["dso", "svo", "okvis", "orb_slam", "lsd_slam", "rovio", "ice_ba"]}
algo2image.update({algo:"zkjoker/image2:19-12-31" for algo in ["vins_mono", "msckf"]})
algo2image.update({algo:"zkjoker/image4:v1" for algo in ["basalt"]})
algo2image.update({algo:"zkjoker/image3:19-12-30" for algo in ["rovio"]})
algo2image.update({algo:"zkjoker/image5:v2" for algo in ["dvo"]})
algo2image.update({algo:"zkjoker/image6:rgbd" for algo in ["rgbdslam"]})
algo2image.update({algo:"zkjoker/laserslam:v4" for algo in ["gmapping","hector_slam","cartographer"]})

algo2datasets = {"vins_mono":["euroc", "eth-aslcla", "ar_box"],
                 "dso":["monoVO"],
                 "svo":["airground_rig"],
                 "okvis":["euroc"],
                 "orb_slam":["tum", "kitti", "euroc"],
                 "lsd_slam":["lsd_room"],
                 "rovio":["euroc"],
                 "basalt":["euroc", "tumvi"],
                 "ice_ba":["euroc"],
                 "msckf":["euroc"],
                 "dvo":["tum"],
                 "rgbdslam":["tum"],
                 "gmapping":["control_instructions"],
                 "hector_slam":["control_instructions"],
                 "cartographer":["control_instructions"]}


def main(config):

    if config.algo_dataset in type2algos["全部"]:
        print("available datasets for {}: {}".format(config.algo_dataset, algo2datasets[config.algo_dataset]))
        return
    if config.algo is None:
        print("Please specify an algorithm")
        return
    if config.dataset is None or not config.dataset in algo2datasets[config.algo]:
        print("Please specify an dataset in {}".format(algo2datasets[config.algo]))
        return
    print("Running slam, you can press ctrl+c to stop it")
    subprocess.Popen(docker_cmd.format(algo2image[config.algo], config.algo, config.dataset), shell=True)

    def signal_handler(sig, frame):
        print('You pressed Ctrl+C! Stopping running...')
        subprocess.Popen("docker stop --time 1 slam_from_qt", shell=True)
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    print('Press Ctrl+C')
    signal.pause()



if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--algo', type=str, choices=type2algos["全部"], help='algorithm to run')
    parser.add_argument('--dataset', type=str,
                        help='dataset to run, you\'d better use \'--algo_dataset\' to see which datasets are available')
    parser.add_argument('--algo_dataset', type=str, choices=type2algos["全部"],
                        help='pass algorithm to see which datasets are available for it')
    config = parser.parse_args()

    main(config)

