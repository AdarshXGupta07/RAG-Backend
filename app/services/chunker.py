def chunk_text(text:str,chunk_size:int =1000,overlap:int =150):
    start=0;
    chunks=[]
    while(start<len(text)):
        end=start+chunk_size
        chunk=text[start:end]
        chunks.append(chunk)
        start+=chunk_size-overlap
    return chunks