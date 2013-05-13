/******************************************************************************* 
@All Right Reserved (C), 2010-2100, golaxy.cn
Filepath   : E:\Project\IctClas\ictclas5
Filename   : ICTCLAS5.h
Version    : ver 5.0
Author     : x10n6y@gmail.com 
Date       : 2010/06/03  
Description:    
History    :
             1.2010/06/03 17:19 Created by x10n6y@gmail.com Version 5.0  

*******************************************************************************/
#ifndef ICTCLAS_LIB_
#define ICTCLAS_LIB_

#define ICTCLAS_EXPORTS

#ifdef OS_LINUX
	#define ICTCLAS_API 
#else
	#ifdef ICTCLAS_EXPORTS		
		#define ICTCLAS_API extern "C" __declspec(dllexport)	//export function
	#else
		#define ICTCLAS_API extern "C" //extern , c compiler
	#endif
#endif

//////////////////////////////////////////////////////////////////////////
//标注集
//////////////////////////////////////////////////////////////////////////
#define ICT_POS_MAP_SECOND 0 //计算所二级标注集
#define ICT_POS_MAP_FIRST 1  //计算所一级标注集
#define  PKU_POS_MAP_SECOND 2 //北大二级标注集  
#define PKU_POS_MAP_FIRST 3	//北大一级标注集
#define POS_MAP_NUMBER 4 //标注集 数量 
#define  POS_SIZE 8 // 词性标记最大字节数 

//////////////////////////////////////////////////////////////////////////
// 字符编码类型
//////////////////////////////////////////////////////////////////////////
enum eCodeType {
	CODE_TYPE_UNKNOWN,//type unknown
	CODE_TYPE_ASCII,//ASCII
	CODE_TYPE_GB,//GB2312,GBK,GB10380
	CODE_TYPE_UTF8,//UTF-8
	CODE_TYPE_BIG5//BIG5
};
//////////////////////////////////////////////////////////////////////////
//字符串结果 
//////////////////////////////////////////////////////////////////////////
#pragma pack(1) 
struct tagICTCLAS_Result{
  int iStartPos; //开始位置
  int iLength; //长度
  char szPOS[POS_SIZE];//词性
  int	iPOS; //词性ID
  int iWordID; //词ID
  int iWordType; //词语类型，用户词汇？(0-否,1-是)
  int iWeight;// 词语权重
 };
#pragma pack() 
typedef tagICTCLAS_Result* LPICTCLAS_RESULT;
//////////////////////////////////////////////////////////////////////////
//接口
//////////////////////////////////////////////////////////////////////////
/************************************************************************
* Method:     ICTCLAS_Init<!读取配置文件，加载词典等>
* Parameter:  const char * pszInitDir<!配置文件，及data文件夹所在路径 >
* Returns:      bool<!初始化是否成功>
* Description: 调用其它任何接口前，必须保证本接口调用成功！
* Remark: 1.2010/06/03 17 : 34 created by x10n6y version 5.0 
*************************************************************************/
ICTCLAS_API bool ICTCLAS_Init(const char* pszInitDir=NULL);

/************************************************************************
* Method:     ICTCLAS_Exit<! 退出，释放相关资源>
* Returns:     ICTCLAS_API bool<! 退出是否成功>
* Description:	所有操作完成后，请调用本接口释放相关资源！
* Remark: 1.2010/06/04 9 : 42 created by x10n6y version 5.0 
*************************************************************************/
ICTCLAS_API bool ICTCLAS_Exit();

/************************************************************************
* Method:     ICTCLAS_SetPOSmap<!指定词性标注集>
* Parameter:  int nPOSmap<! 标注集ID>
					 ICT_POS_MAP_FIRST  计算所一级标注集
					 ICT_POS_MAP_SECOND  计算所二级标注集
					 PKU_POS_MAP_SECOND   北大二级标注集
					 PKU_POS_MAP_FIRST 	  北大一级标注集

* Returns:    ICTCLAS_API bool<! 指定成功与否>
* Description: 
* Remark: 1.2010/06/22 11 : 11 created by x10n6y version 5.0 
*************************************************************************/
ICTCLAS_API bool ICTCLAS_SetPOSmap(int nPOSmap);

/************************************************************************
* Method:     ICTCLAS_ImportUserDict<! 导入用户词典文件>
* Parameter:  const char * pszFileName<! 用户词典路径名称>
* Parameter:  e_CodeType codeType<!词典编码类型>
* Returns:      ICTCLAS_API unsigned int<! 成功导入的词汇数量>
* Description: 用户导入词汇文件格式如下：
                        1.词语与词性用‘@@’间隔。例如：“中科院@@nr；
						2.一行一词；
						3.词性可省略

* Remark: 1.2010/06/04 9 : 43 created by x10n6y version 5.0 
************************************************************************/
ICTCLAS_API unsigned int ICTCLAS_ImportUserDictFile(
	const char* pszFileName,
	eCodeType codeType=CODE_TYPE_UNKNOWN
	);

/************************************************************************
* Method:     ICTCLAS_ImportUserDict<! 导入用户词典>
* Parameter: char* pszDictBuffer<! 用户词汇字符串>
					1.词语与词性用‘@@’间隔；
					2.词与词之间用 半角‘;’间隔；
					3.词性可省略
					例如：“中科院@@nr;分词 v;系统@@adj;……;”，
					或者：“中科院;分词;系统;……;”
* Parameter:  e_CodeType codeType<!词典编码类型>
* Returns:      ICTCLAS_API unsigned int<! 成功导入的词汇数量>
* Description: 1.本接口将根据用户输入的词汇，生成相应的用户词典。
                      2.该词典，将覆盖内存里原有的用户词典。
* Remark: 1.2010/06/04 9 : 43 created by x10n6y version 5.0 
************************************************************************/
ICTCLAS_API unsigned int ICTCLAS_ImportUserDict(
								   const char* pszDictBuffer,
								   const int nLength,
								   eCodeType codeType
								   );
/************************************************************************
* Method:     ICTCLAS_SaveTheUsrDic<!保存用户词典>
* Description:1.本接口将会覆盖原有/data/文件夹用户相关词典。  
                     2.用户可在配置文件中，指定下次是否使用该词典。
*
* Remark: 1.2010/07/05 16 : 16 created by x10n6y version 2.0 
*************************************************************************/
ICTCLAS_API int ICTCLAS_SaveTheUsrDic();

/************************************************************************
* Method:     ICTCLAS_ParagraphProcess<! 分词，返回结果为字符串>
* Parameter:  const char * pszText<!需要分词的文本内容>
* Parameter:  int iLength<!需要分词的文本长度>
* Parameter:  char*	pszResult [out]<!分词结果字符串>
* Parameter:  e_CodeType codeType<!字符编码类型>
* Parameter:  int bEnablePOS<！是否词性标注 >
* Returns:      ICTCLAS_API int<! 结果字符串长度>
* Description: 调用本接口，由用户分配内存，保存结果（pszResult）
，建议内存大小strlen(pszText)*6！
* Remark: 1.2010/06/22 11 : 11 created by x10n6y version 5.0 
*************************************************************************/
ICTCLAS_API int ICTCLAS_ParagraphProcess(
	const char*  pszText,
	int			    iLength,
	char*		    pszResult, //[out]
	eCodeType	codeType=CODE_TYPE_UNKNOWN,
	bool		        bEnablePOS=false
	);
/************************************************************************
* Method:     ICTCLAS_ParagraphProcessA<! 分词，返回结果为字符串结构数组>
* Parameter:  const char * pszText<! 需要分词的文本内容>
* Parameter:  int iLength<! 需要分词的文本长度>
* Parameter:  int & nResultCount [out]<! 结果数组长度>
* Parameter:  e_CodeType codeType<! 字符编码类型>
* Parameter:  int bEnablePOS<! 是否词性标注>
* Returns:      ICTCLAS_API t_pRstVec<! 结果数组>
* Description: 
                      调用此接口后，应调用ICTCLAS_ResultFree() 释放相关内存。
* Remark: 1.2010/06/22 11 : 11 created by x10n6y version 5.0 
*************************************************************************/
ICTCLAS_API LPICTCLAS_RESULT  ICTCLAS_ParagraphProcessA(
	const char*  pszText,
	int			    iLength,
	int			    &nResultCount, //[out]
	eCodeType	codeType=CODE_TYPE_UNKNOWN,
	bool		        bEnablePOS=false
	);


/************************************************************************
* Method:       ICTCLAS_ResultFree<! 释放结果内存>
* Parameter:   t_pRstVec pRetVec<!要释放的结果数组 >
* Returns:       ICTCLAS_API bool<! 释放成功与否>
* Description: 本接口用于释放 ICTCLAS_ParagraphProcessA 生成的结果内存
* Remark: 1.2010/06/22 11 : 11 created by x10n6y version 5.0 
*************************************************************************/
ICTCLAS_API bool ICTCLAS_ResultFree(LPICTCLAS_RESULT pRetVec);



/************************************************************************
* Method:     ICTCLAS_FileProcess<!文本文件分词>
* Parameter:  const char * pszSrcFileName<!要分词的文件>
* Parameter:  const char * pszDstFileName<! 结果文件存放位置>
* Parameter:  e_CodeType srcCodeType<!要处理的文本编码类型>
* Parameter:  bool bEnablePOS<! 是否词性标准>
* Returns:      ICTCLAS_API bool<! 分词是否成功>
* Description: 1.用户若不指定分词结果保存位置，系统将结果保存至
                        当前目录下，test_result.txt 中。
					 2.pszDstFileName若该文件不存在， 则自动生成;
					    否则先清空已有内容。
* Remark: 1.2010/06/22 11 : 11 created by x10n6y version 5.0 
*************************************************************************/
ICTCLAS_API bool ICTCLAS_FileProcess(
									 const char* pszSrcFileName,
									 const char* pszDstFileName, 
									 eCodeType	srcCodeType=CODE_TYPE_UNKNOWN,
									 bool		        bEnablePOS=false
									 );

/************************************************************************
* Method:      ICTCLAS_ParagraphProcessAW<!C# 接口>
* Parameter:  const char * pszText<! 要处理的文本>
* Parameter:  LPICTCLAS_RESULT pResult<! 结果数组>
* Parameter:  eCodeType codeType<! 文本编码类型>
* Parameter:  bool bEnablePOS<! 是否词性标注>
* Returns:      ICTCLAS_API int<! 结果数组长度>
* Description:  结果数组内存空间，用户不需做任何处理。
*
* Remark: 1.2010/07/05 16 : 16 created by x10n6y version 2.0 
*************************************************************************/
ICTCLAS_API int ICTCLAS_ParagraphProcessAW(
	const char*               pszText,
	LPICTCLAS_RESULT  pResult,
	eCodeType	             codeType=CODE_TYPE_UNKNOWN,
	bool	  	                     bEnablePOS=false
	);
#endif // ICTCLAS_LIB_

