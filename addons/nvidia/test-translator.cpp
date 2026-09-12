// Candidate ABI/correctness self-test, not a performance benchmark.
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <GLES2/gl2.h>
#include "ShaderTranslator.h"
struct Guarded { uint64_t before[8]; ST_BuiltInResources value; uint64_t after[8]; };
int main() {
 Guarded g{};for(int i=0;i<8;++i){g.before[i]=0x1122334455667788ULL;g.after[i]=0x8877665544332211ULL;}
 STInitialize();STGenerateResources(&g.value);
 for(int i=0;i<8;++i)if(g.before[i]!=0x1122334455667788ULL||g.after[i]!=0x8877665544332211ULL){std::fputs("ABI overwrite\n",stderr);return 1;}
 if(g.value.MaxVertexAttribs<=0||g.value.MaxDrawBuffers<=0)return 2;
 const char* shaders[]={"attribute vec4 a; void main(){gl_Position=a;}","precision mediump float; void main(){gl_FragColor=vec4(1.0,0.0,0.0,1.0);}"};
 for(int i=0;i<2;++i){ST_ShaderCompileInfo in{};in.type=i?GL_FRAGMENT_SHADER:GL_VERTEX_SHADER;in.spec=ST_GLES2_SPEC;in.output=ST_GLSL_330_CORE_OUTPUT;in.compileOptions=ST_OBJECT_CODE;in.pResources=&g.value;in.pShaderString=shaders[i];ST_ShaderCompileResult* result=nullptr;STCompileAndResolve(&in,&result);if(!result||!result->compileStatus||!result->translatedSource||!std::strstr(result->translatedSource,"void main")){if(result)std::fprintf(stderr,"Compile failure: %s\n",result->infoLog);return 3;}STFreeShaderResolveState(result);}
 STFinalize();std::printf("PASS legacy resource ABI guard, sizeof=%zu; vertex+fragment GLSL translation\n",sizeof(ST_BuiltInResources));return 0;
}
