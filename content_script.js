function addScoreLabelToThread(num)
{
	var title_block = document.getElementsByClassName('entry')[0];
	var p = document.createElement("p");
	p.innerText = 'The average mood of this thread is: ' + num.toString();
	title_block.appendChild(p);
}
addScoreLabelToThread(5);
