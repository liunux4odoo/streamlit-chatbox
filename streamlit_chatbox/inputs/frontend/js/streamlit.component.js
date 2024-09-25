var _last_args=null;

function sendMessageToStreamlitClient(type,data){
    var outData=Object.assign({
        isStreamlitMessage:true,
        type:type
    },data);
    window.parent.postMessage(outData,'*');
}

function initStreamlit(){
    sendMessageToStreamlitClient('streamlit:componentReady',{apiVersion:1});
}

function setFrameHeight(height){
    sendMessageToStreamlitClient('streamlit:setFrameHeight',{height:height});
}

function sendDataToPython(data,type='json'){
    sendMessageToStreamlitClient('streamlit:setComponentValue',{value:data,dataType:type});
}

function onDataFromPython(args){
    console.log(args);
}

function _onDataFromPython(e){
    // console.log(e);
    if(e.data.type!=='streamlit:render') return;
    if(! _.isEqual(_last_args,e.data.args)){
        onDataFromPython(e.data.args);
        _last_args=e.data.args;
    }
}

window.addEventListener('message',_onDataFromPython);

window.addEventListener('load',function(){
    window.setTimeout(function(){
        setFrameHeight(document.documentElement.clientHeight);
    },100);
})

window.addEventListener('resize',function(){
    window.setTimeout(function(){
        setFrameHeight(document.documentElement.clientHeight);
    },100);
})