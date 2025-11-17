%displays edges matrix on image

function BinaryImage(file)

%reads edges from text file
edgesNew = readmatrix(file, 'OutputType', 'string');

%converts edges to decimals
edgesMatrices = arrayfun(@bin2dec, edgesNew);

%shows edges
imshow(edgesMatrices/255);

end