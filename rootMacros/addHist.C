template <typename T>
T* AddHist(const T* hist1,const T* hist2){
	T* sum = (T*)hist1 -> Clone();
	sum -> Add(hist2);

	sum -> SetStats(0);

	return sum;
}


