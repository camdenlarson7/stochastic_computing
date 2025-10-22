%performs Roberts Edge Detection to display a processed grayscale image

%converting image to matrix of intensities
A = imread('smallmountains.jpg')
AA = rgb2gray(A)
B = double(AA)

%displaying grayscale of original image
figure
imshow(B/255)

%creating matrix of edges
[rows, columns] = size(B)
edges = [rows - 1, columns - 1]

%setting edge values based on Roberts Edge Detection algorithm
edges = abs(B(1:end-1, 1:end-1) - B(2:end, 2:end)) + abs(B(1:end-1, 2:end) - B(2:end, 1:end-1))

%displaying processed image
figure
imshow(edges/255)