class GeometryError(Exception):
    pass


class InvalidPointError(GeometryError):
    pass


class DegenerateLineError(GeometryError):
    pass


class InvalidShapeError(GeometryError):
    pass

class Point2D:
    def __init__(self,x,y):
        if not isinstance(x,(int,float)) or not isinstance(y,(int,float)):
            raise InvalidPointError("Point coordinates must be numbers")
        self.x=x
        self.y=y

    def distance_to(self,other):
        return ((self.x-other.x)**2+(self.y-other.y)**2)** 0.5

    def translate(self,dx,dy):
        return Point2D(self.x+dx,self.y+dy)

    def midpoint(self,other):
        return Point2D((self.x+other.x)/2,
                       (self.y+other.y)/2)
    def __str__(self):
        return f"Point({self.x},{self.y})"


class Line2D:
    def __init__(self, p1, p2):
        if p1.x == p2.x and p1.y == p2.y:
            raise DegenerateLineError("A line needs two distinct points")
        self.p1 = p1
        self.p2 = p2

    def length(self):
        return self.p1.distance_to(self.p2)

    def slope(self):
        if self.p1.x==self.p2.x:
            return None
        return (self.p2.y-self.p1.y)/(self.p2.x-self.p1.x)

    def is_parallel(self, other):
        return self.slope()==other.slope()

    def is_perpendicular(self, other):
        s1=self.slope()
        s2=other.slope()
        if s1 is None and s2==0:
            return True
        if s2 is None and s1==0:
            return True
        if s1 is not None and s2 is not None:
            return s1*s2==-1
        return False

    def __str__(self):
        return f"Line({self.p1},{self.p2})"




class Circle:
    def __init__(self,center,radius):
        if radius<=0:
            raise InvalidShapeError("Radius must be positive")
        self.center=center
        self.radius=radius

    def area(self):
        return 3.1415926535*self.radius*self.radius
    def circumference(self):
        return 2*3.1415926535*self.radius
    def contains(self, point):
        return self.center.distance_to(point)<=self.radius
    def __str__(self):
        return f"Circle(Center={self.center}, Radius={self.radius})"
    

class Triangle:
    def __init__(self,p1,p2,p3):
        if self._are_collinear(p1,p2,p3):
            raise InvalidShapeError("Points cannot be collinear")
        self.p1=p1
        self.p2=p2
        self.p3=p3
    def _are_collinear(self,p1,p2,p3):
        return (p1.x*(p2.y-p3.y)+p2.x*(p3.y-p1.y)+p3.x*(p1.y-p2.y))==0

    def area(self):
        return abs(
            (self.p1.x*(self.p2.y-self.p3.y)+self.p2.x*(self.p3.y-self.p1.y)+self.p3.x*(self.p1.y-self.p2.y))/2)

    def centroid(self):
        return Point2D(
            (self.p1.x+self.p2.x+self.p3.x)/3,(self.p1.y+self.p2.y+self.p3.y)/3)

    def __str__(self):
        return f"Triangle({self.p1}, {self.p2}, {self.p3})"
    


    




    
    



    
    
        























    
    
        
            
    
    
