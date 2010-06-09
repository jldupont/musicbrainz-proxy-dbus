"""
    Filter
    
    @author: jldupont
    @date: Jun 8, 2010
"""

__all__=["filterArtist"]

_artistPatterns=["", "various", "various artist", "various artists", "original soundtrack", "soundtrack"]

def filterArtist(artist_name):
    try:
        lu=unicode(artist_name, "utf-8")    
        l=lu.lower()
    except: return False
        
    return l in _artistPatterns