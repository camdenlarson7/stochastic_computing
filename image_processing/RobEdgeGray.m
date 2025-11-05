%performs Roberts Edge Detection to display a processed grayscale image

function RobEdgeGray(img)

%converting image to matrix of intensities
image = imread(img);
grayImage = rgb2gray(image);
B = double(grayImage);

%displaying grayscale of original image
figure;
imshow(B/255);

%creating matrix of edges
[rows, columns] = size(B);
edges = [rows - 1, columns - 1];

%setting edge values based on Roberts Edge Detection algorithm
edges = abs(B(1:end-1, 1:end-1) - B(2:end, 2:end)) + abs(B(1:end-1, 2:end) - B(2:end, 1:end-1));

%displaying processed image
figure;
imshow(edges/255);

%creating empty image matrix
imageMatrix = strings(size(B));

[rows,cols] = size(B);

%filling image matrix with binary values
for i = 1:rows
    for j = 1:cols
        imageMatrix(i,j) = dec2bin(B(i,j), 8);
    end
end

%outputting image matrix to a text file
writematrix(imageMatrix, 'imageMatrix.txt');

end