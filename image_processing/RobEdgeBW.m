%performs Roberts Edge Detection to display a processed black and white image

%converting image to matrix of intensities
A = imread('smallmountains.jpg')
AA = rgb2gray(A)
B = double(AA)

%displaying grayscale of original image
figure
image(B)
colormap(gray(256))
axis('image')

C = edge(B, 'roberts')

figure
image(uint8(C)*255)
colormap(gray(256))
axis('image')