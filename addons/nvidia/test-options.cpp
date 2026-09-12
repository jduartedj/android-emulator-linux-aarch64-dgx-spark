#include <cstdint>
#include <cstdio>
#include <cstring>
#include <cassert>
#include <GLES2/gl2.h>
#include "ShaderTranslator.h"
#include "GLSLANG/ShaderLang.h"
int main(){
 struct G { uint64_t a[8]; ST_BuiltInResources r; uint64_t b[8]; } g;
 memset(&g,0xA5,sizeof(g));STInitialize();STGenerateResources(&g.r);
 auto run=[&](ST_CompileOptions opts){ST_ShaderCompileInfo in{};in.type=GL_VERTEX_SHADER;in.spec=ST_GLES2_SPEC;in.output=ST_GLSL_330_CORE_OUTPUT;in.compileOptions=opts;in.pResources=&g.r;in.pShaderString="void main(){float x; gl_Position=vec4(x);}";ST_ShaderCompileResult* o=nullptr;STCompileAndResolve(&in,&o);assert(o);return o;};
 auto out=run(ST_OBJECT_CODE|ST_INITIALIZE_UNINITIALIZED_LOCALS);assert(out->compileStatus);bool initialized=strstr(out->translatedSource,"x = 0.0")||strstr(out->translatedSource,"x=0.0");if(!initialized){puts("FAIL legacy bit31 did not initialize local");return 3;}STFreeShaderResolveState(out);puts("PASS legacy bit31 maps to modern initialization");
 const uint64_t supported=ST_OBJECT_CODE|ST_VARIABLES|ST_INITIALIZE_UNINITIALIZED_LOCALS;
 for(unsigned b=0;b<64;++b){if(supported&(1ULL<<b))continue;out=run(ST_OBJECT_CODE|(1ULL<<b));assert(!out->compileStatus);assert(strstr(out->infoLog,"Unsupported legacy"));STFreeShaderResolveState(out);}
 out=run(ST_OBJECT_CODE|ST_VARIABLES);assert(out->compileStatus);STFreeShaderResolveState(out);
 for(int i=0;i<8;++i)assert(g.a[i]==0xA5A5A5A5A5A5A5A5ULL&&g.b[i]==0xA5A5A5A5A5A5A5A5ULL);
 STFinalize();puts("PASS base caller mask, all61unsupported bits rejected, resource canary intact");
}
