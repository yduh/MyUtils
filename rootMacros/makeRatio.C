
template <typename T>
T* makeRatio(const T* num,const T* dem){
	T* ratio = (T*)num -> Clone();
	ratio -> Divide(dem);

	ratio -> SetStats(0);

	return ratio;
}


