let sliceArc = 45;
let lastDeg = 0;
const spinner = document.getElementById('spinner');
function spinIt() {
/*   // Avoid spinning before the end of the current round
  const disableSpin = () => document.getElementById('spin-btn').style.pointerEvents = 'none';
  disableSpin();
  setTimeout(() => {
    document.getElementById('spin-btn').style.pointerEvents = 'visible';
  }, 6000); */
  
  // calculate spin degree
  let stepDeg = Math.floor(Math.random() * 360) + 1;
  let degree = stepDeg + 3600 + lastDeg;
  spinner.style.transform = `rotate(${-degree}deg)`;
  lastDeg = degree;
}