function request(subreddit,id){
    $('#data-group').hide();
    $('#loading').show();
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
    var HEIGHT=200;
    var WIDTH=200;
    var radius=Math.min(HEIGHT,WIDTH)/2;
    var color = ['#00ff00','#FFBF00','#8B0000'];
    
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
    $('#loading').hide();
    $('#data-group').show();
}


function get_domain_name(url)
{ 
    var matches = url.match(/:\/\/(?:www\.)?(.[^/]+)(.*)/);
    if(matches.length<=1) {
        return [];
    }
    return [matches[1], matches[2]]
}

chrome.tabs.query({'active': true, 'lastFocusedWindow': true}, function (tabs) {
    var url = tabs[0].url;
    domain_parts = get_domain_name(url);
    var failed = false;
    if (domain_parts.length <=1 || domain_parts[0]!='reddit.com')
    {
        failed = true;
    }
    path_parts = domain_parts[1].split('/');
    if (path_parts[3] != 'comments')
    {
        failed = true;
    }
    if ( !failed ) {
        request(path_parts[2], path_parts[4]);
    } else {
        $('#error').show();
    }
});
