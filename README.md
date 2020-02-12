# О проекте
Прямоугольная укладка графа - это планарная укладка графа на плоскости, при которой выполняются следующие условия:
 - все внутренние грани являются прямоугольниками
 - внешний "контур" графа (т.е. объединение всех внутренних граней) также является прямоугольником
 - все ребра являются отрезками, параллельными осям координат

![Прямоугольная укладка графа](https://github.com/bokoveg/rectangular_graph_drawing/blob/master/doc/rectangular_drawing.jpg)


Предложенная библиотека позволяет строить прямоугольную укладку для некоторого семейства графов (подробнее об ограничения см. в других разделах)

# Теоретические результаты

В 1984 в статье [1] было предложено необходимое и достаточно условие на существование прямоугольной укладки графа без вершин степени 4. Предложенный в статье алгоритм, однако, имел сложность O(n^3), где n - количество вершин в графе.

В 1998 году в статье [2] был предложен линейный алгоритм, который по заданной планарной укладке графа и заданным четырём угловым вершинам строит укладку за линейное время. Этот алгоритм взят за основу в проекте.

В 2002 году в статье [3] был предложен алгоритм выбора четырёх угловых вершин за линейное время, что в сумме с предыдущим пунктом позволяет строить прямоугольную укладку любого графа, удовлетворяющего критерию из [1] за линейной время.
Алгоритм выбора угловых вершин будет реализован в более поздних версиях.

# Описание алгоритма

На вход алгоритм принимает граф, его планарную укладку (embedding) и 4 вершины, которые станут угловыми. Вершины должны быть перечислены в порядке NW, NE, SE, SW.

### Поиск ориентации ребер

На первом этапе алгоритм пытается найти ориентацию всех ребер (горизонтальная или вертикальная). Для этого алгоритм находит будущие границы укладки при помощи обхода в глубину против часовой стрелки. Знание о вершинах позволяет понять, с какой стороны (N, S, E или W) будут находится ребра на границе.

На следующем этапе алгоритм размечает все простые пути, дополняющие часть границы до грани. Такие пути размечаются парой меток, соответвующих границам, на которых заканчивается путь (например, NN, SW, EW и т.д.).

Если среди размеченных путей нашелся путь, отмеченный противоположными метками (EW, WE, NS или SN), то разделив граф по этому пути на 2 части, мы сведем задачу к графу меньшего размера.

В противном случае алгоритм завершается. Следует отметить, что в оригинальной статье предлжен способ разбиения графа не только по "диаметральному" пути, но и по путям с концами на смежных границах. Этот метод будет реализован в более поздних версиях.

### Направление ребра
Одновременно с поиском ориентации ребер можно для каждого ребра определить какая из смежных ему вершин находится выше (или левее). Это возможно за счет фиксации угловых вершин и разметки "диаметрального" пути.

### Вычисление координат
После вычисления ориентации всех ребер необходимо найти координаты вершин графа. Рассмотрим, как вычислить y-координату (для x-координаты аналогично).

![Удаление ребер](https://github.com/bokoveg/rectangular_graph_drawing/blob/master/doc/edge_remove.png)

Построим остовное дерево графа, удалив из него все вертикальные ребра, из нижней вершины которых, выходит ребро влево (такие ребра можно найти, т.к. на предыдущем этапе мы определили направление ребра). Теперь запустив из NE-вершины обход в глубину против часовой стрелки можно посчитать y-координату каждой вершины при помощи динамического программирования.



# Примеры и запуск тестов

# Документация

# Известные проблемы
1. Алгоритм некорректно работает для случаев, когда построить "диаметральный" разделяющий путь не удалось.
2. Сложность алгоритма O(n^2)
3. Необходимость указывать 4 угловые вершины

# Цитирование
[1] C.Thomassen, Plane representations of graphs

[2] Md. Saidur Rahman, Shin-ichi Nakano, Takao Nishizeki, Rectangular grid drawings of plane graphs

[3] M. S. Rahman, S. Nakano and T. Nishizeki, Rectangular drawings of planegraphs without designated corners,Comp.  Geom.  Theo.  and  Appl., 21(3),pp. 121-138, 2002
