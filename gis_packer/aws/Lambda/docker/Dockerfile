FROM amazonlinux

# Update env
WORKDIR /
RUN yum update -y

# Install Zip
RUN yum install -y zip

# Upgrade pip
RUN yum install python3-dev python3-pip python3-wheel -y
RUN pip3 install --upgrade pip

# Install python packages
RUN mkdir -p /packages/my-pkgs/
COPY requirements.txt /packages/requirements.txt
RUN pip3 install -r /packages/requirements.txt -t /packages/my-pkgs/

# IF OPENCV : Remove files not needed
WORKDIR /packages/my-pkgs/cv2/data/
RUN rm -r *.xml

# Create zip files for Lambda Layer deployment
WORKDIR /packages/my-pkgs/
RUN zip -r9 "/packages/lambda-layer.zip" .
WORKDIR /packages/
RUN rm -rf /packages/my-pkgs/

# Reset work dir
WORKDIR /
