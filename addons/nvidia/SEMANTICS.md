# Legacy compile-option boundary: supported and rejected

The frozen base's inspected production shader parser constructs `ST_ShaderCompileInfo` with **ST_OBJECT_CODE | ST_VARIABLES**. NoothercompileAndResolvecallsitewasfoundintheinspectedgfxstreamhostC++sources. Thisboundsobservedusebutdoesnotjustifyuncheckedforwarding.

This successor explicitly maps:

| Legacy option | Legacy bit | Modern meaning |
|---|---:|---|
| ST_OBJECT_CODE |2|SH_OBJECT_CODE |
| ST_VARIABLES |3|SH_VARIABLES |
| ST_INITIALIZE_UNINITIALIZED_LOCALS |31|SH_INITIALIZE_UNINITIALIZED_LOCALS, bit29 |

All remaining61bitpositions are rejected with a safely allocated/freeable failure result, falsecompileStatus, emptytranslatedSource and an unsupported-option infoLog. No unknownbit is ignored or interpreted underanothermodernmeaning. The rawstatic_cast forwarding was removed.

Independent review demonstrated the priorlibrary left `float x;` uninitializedwithlegacybit31. The newred/greentest failsagainstpriornormalizedlibrary and passesagainstthesuccessor (`float x = 0.0;`), then testsall61unsupportedbits/callermask/canary. Theoldmodernbit29shortcut is now correctlyunsupportedthroughthislegacyboundary. Resourceconversion,canary,vertex/fragmenttranslationandnestedcopy/destroytestsremain.

No generalimplementationofeveryoldANGLEoptionisclaimed. Ifafuturebasecallerrequiresanotherlegacyflag,itmustbeexplicitlymapped/testedandversioned; don'tremoveguard orforwardrawmask. Unknownoptionsfailclosed, notsilentfallback. Newbinaryhasnewhash/actualGPUrunbinding; originalbenchmarkdataretainedashistorical.
