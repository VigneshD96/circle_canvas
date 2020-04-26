let width = 0 , height = 0, timeOutId, originX=0, originY=0,
maxCircleRadius = 20, colours = ['#233342','#ce8054', '#5a6882'];
canvas = document.getElementsByTagName("canvas")[0];
var getRandomRoundNumberTill = limit => Math.ceil(Math.random()*limit);
function deBounce(callbackFn){
    clearTimeout(timeOutId);
    timeOutId = setTimeout(()=>{
        callbackFn();
    },50);
}
function resizeCanvas(){
    width = window.innerWidth;
    height = window.innerHeight;
    canvas.width = width;
    canvas.height = height;
}
window.addEventListener('resize',()=> {deBounce(resizeCanvas)});
resizeCanvas();

let context = canvas.getContext('2d');
// context.fillRect(x,y, 100, 100);
class Circle {
    constructor({ x, y, radius }) {
        this.x = x;
        this.y = y;
        this.dx = Math.ceil((Math.random()-0.5)*5) || 1;
        this.dy = Math.ceil((Math.random()-0.5)*5) || 1;
        this.startAngle = 0;
        this.endAngle = 2 * Math.PI;
        this.radius = (radius)? radius : 2;
        this.backupRadius=this.radius;
        this.color=colours[Math.floor((Math.random()*10)%3)]
        // this.color = `rgb(${getRandomRoundNumberTill(255)},${getRandomRoundNumberTill(255)},${getRandomRoundNumberTill(255)})`;
    }
    draw = () => {
        context.beginPath();
        context.fillStyle=this.color;
        context.arc(this.x, this.y, this.radius, 0, Math.PI * 2, false);
        context.fill();
        context.closePath();
    };
    update = () => {
        if (this.x >= width - this.radius || this.x <= originX + this.radius)
            this.dx = -this.dx;
        if (this.y >= height - this.radius || this.y <= originY + this.radius)
            this.dy = -this.dy;
        this.draw();
        this.x += this.dx;
        this.y += this.dy;
    };
    getDistanceBetweenPoints(x1,y1,x2,y2){
        return Math.hypot(x1-x2,y1-y2);
    }
    currentPointInside(x,y,maxDistance){
        let distance = this.getDistanceBetweenPoints(this.x, this.y, x, y);
        if(distance <= maxDistance)
            this.radius = this.backupRadius + (this.backupRadius * (1 - distance/maxDistance) * 5);
        else
            this.radius=this.backupRadius;
    }
}
function getRandomCircleFeatures(){
    let r=getRandomRoundNumberTill(maxCircleRadius);
    return{
        x : Math.random()*(width-2*r) + r,
        y : Math.random()*(height-2*r) + r,
        radius : r
    }
}
circleArray=[];
for (let index = 0; index < 500; index++) {
    circleArray.push(new Circle(getRandomCircleFeatures()));
}
var mouseX=0, mouseY=0, buffer=150;
function start(){
    context.clearRect(originX, originY, width, height);
    for (let index = 0; index < circleArray.length; index++) {
        circleArray[index].currentPointInside(mouseX, mouseY, buffer);
        circleArray[index].update();
    }
    requestAnimationFrame(start);
}
start();
canvas.addEventListener('mousemove',(e)=>{
    mouseX=e.clientX;
    mouseY=e.clientY;
})