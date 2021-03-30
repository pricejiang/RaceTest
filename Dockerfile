ARG CUDA_VERSION=11.2.0
ARG ROS_VERSION='noetic'
FROM nvidia/cudagl:${CUDA_VERSION}-base-ubuntu20.04
ENV DEBIAN_FRONTEND=noninteractive
ENV NVIDIA_DRIVER_CAPABILITIES compute,graphics,utility
RUN sh -c 'echo "deb http://packages.ros.org/ros/ubuntu focal main" > /etc/apt/sources.list.d/ros-latest.list'
RUN apt-key adv --keyserver 'hkp://keyserver.ubuntu.com:80' --recv-key C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654
ARG ROS_VERSION
RUN apt-get update && apt-get install -y --no-install-recommends \
  libx11-xcb-dev \
  libxkbcommon-dev \
  libwayland-dev \
  libxrandr-dev \
  libegl1-mesa-dev \
  libsdl2-2.0 \
  xserver-xorg \
  python-is-python3 \
  python3-pip \
  ros-$ROS_VERSION-desktop \
  python3-rosdep \
  python3-rosinstall \
  python3-rosinstall-generator \
  python3-wstool \
  build-essential \
  ros-$ROS_VERSION-ackermann-msgs \
  ros-$ROS_VERSION-tf \
  ros-$ROS_VERSION-derived-object-msgs \
  ros-$ROS_VERSION-cv-bridge \
  ros-$ROS_VERSION-pcl-conversions \
  ros-$ROS_VERSION-pcl-ros \
  ros-$ROS_VERSION-rqt-gui-py \
  ros-$ROS_VERSION-rviz \
  python3-osrf-pycommon \
  python3-catkin-tools \
  git-all \
  unzip \
  vim \
  wget && \
  rm -rf /var/lib/apt/lists/*
RUN pip3 install pygame
RUN pip3 install simple_pid
RUN useradd -m carla
RUN touch /etc/asound.conf && echo "pcm.!default { \
                  type plug \
                  slave.pcm 'null' \
                  }" > /etc/asound.conf
RUN rosdep init && rosdep update
RUN echo "carla:carla" | chpasswd && adduser carla sudo
USER carla
WORKDIR /home/carla
RUN cd /home/carla && mkdir carla-simulator && cd carla-simulator && wget https://carla-releases.s3.eu-west-3.amazonaws.com/Linux/CARLA_0.9.11.tar.gz && tar -xvzf CARLA_0.9.11.tar.gz && rm CARLA_0.9.11.tar.gz
# Select the video driver between offsreen and x11
# x11 is recommended for vulkan support
# RUN /bin/bash -c 'source /opt/ros/$ROS_VERSION/setup.bash; cd /home/carla; mkdir -p carla-ros-bridge/catkin_ws/src; cd carla-ros-bridge; git clone https://github.com/carla-simulator/ros-bridge.git; cd ros-bridge; git submodule update --init; cd ../catkin_ws/src; ln -s ../../ros-bridge; cd ..; rosdep update; rosdep install --from-paths src --ignore-src -r; catkin_make'
USER root
RUN /bin/bash -c 'mkdir -p /home/carla/carla-ros-bridge/catkin_ws/src && cd /home/carla/carla-ros-bridge; \
git clone --recurse-submodules https://github.com/carla-simulator/ros-bridge.git catkin_ws/src/ros-bridge; \
source /opt/ros/noetic/setup.bash; \
cd catkin_ws; \
rosdep update; \
rosdep install --from-paths src --ignore-src -r; \
catkin_make'

RUN chown carla:carla /home/carla/carla-ros-bridge 
# RUN sed -i 's/0.9.10/0.9.11/g' /home/carla/carla-ros-bridge/ros-bridge/carla_ros_bridge/src/carla_ros_bridge/bridge.py
USER carla
RUN echo "source /opt/ros/noetic/setup.bash \n\
export PYTHONPATH=$PYTHONPATH:/home/carla/carla-simulator/PythonAPI/carla/dist/carla-0.9.11-py3.7-linux-x86_64.egg \n\
source /home/carla/carla-ros-bridge/catkin_ws/devel/setup.bash" >> /home/carla/.bashrc

RUN mkdir graic-workspace
ENV SDL_VIDEODRIVER=x11
