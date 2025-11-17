%displays edges matrix on image

function StochasticImage(file)

%reads edges from text file
edges = readmatrix(file, 'OutputType', 'string');

[rows,columns] = size(edges);
edgesMatrix = zeros(rows,columns);

for i = 1:rows
    for j = 1:columns
        onesCount = 0;
        tempString = char(edges(i,j));
        onesCount = sum(tempString == '1');
        value = onesCount / strlength(tempString);
        edgesMatrix(i, j) = value;
    end
end

%shows edges
imshow(edgesMatrix);
writematrix(edgesMatrix, 'edgesStochastic.txt');

end