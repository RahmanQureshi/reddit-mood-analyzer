function request(subreddit,id){
    var count=[0,0,0];
    var average=0;
    $.get('/'+subreddit+'/'+id,function(data,status){
        if(status=='success'){
            for(var i=0;i<data.length;i++){
                average+=data[i];
                if(data[i]>0&&data[i]<1){
                    count[0]+=1;
                }
                else if(data[i]==0){
                    count[1]+=1;
                }
                else{
                    count[2]+=1
                }
            }
            average=average/parseFloat(data.length);
            pieChart(count);
        }
    });
}

function pieChart(data){
    $('#loading').hide();
    var HEIGHT=300;
    var WIDTH=300;
    var radius=Math.min(HEIGHT,WIDTH)/2;
    var color = ['#00ff00','#ffff00','#ff0000'];
    
    var svg = d3.select('.visual-box')
    .append('svg')
    .attr('width', WIDTH)
    .attr('height', HEIGHT)
    .append('g')
    .attr('transform', 'translate('+(WIDTH/2)+','+(HEIGHT/2)+')'); 
    
    var arc = d3.svg.arc().outerRadius(radius);
    
    var pie = d3.layout.pie()
    .value(function(d){return d})
    .sort(null);
    
    var path = svg.selectAll('path')
    .data(pie(data))
    .enter()
    .append('path')
    .attr('d', arc)
    .attr('fill', function(d,i){return color[i]});
}

pieChart([1,2,3]);