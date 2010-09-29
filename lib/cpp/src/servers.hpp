#ifndef AGNOS_SERVERS_HPP_INCLUDED
#define AGNOS_SERVERS_HPP_INCLUDED

#include "objtypes.hpp"
#include "utils.hpp"
#include "transports.hpp"
#include "transport_factories.hpp"
#include "protocol.hpp"


namespace agnos
{
	namespace servers
	{
		using agnos::protocol::BaseProcessor;
		using agnos::protocol::IProcessorFactory;
		using agnos::transports::ITransport;
		using agnos::transports::factories::ITransportFactory;
		using agnos::transports::factories::SocketTransportFactory;


		DEFINE_EXCEPTION(SwitchError);

		class BaseServer
		{
		protected:
			IProcessorFactory& processor_factory;
			shared_ptr<ITransportFactory> transport_factory;

			virtual void serve_client(shared_ptr<BaseProcessor> proc) = 0;

		public:
			BaseServer(IProcessorFactory& processor_factory, shared_ptr<ITransportFactory> transport_factory);
			virtual void serve();
			virtual void close();
		};


		//////////////////////////////////////////////////////////////////////

		class SimpleServer : public BaseServer
		{
		protected:
			virtual void serve_client(shared_ptr<BaseProcessor> proc);

		public:
			SimpleServer(IProcessorFactory& processor_factory, shared_ptr<ITransportFactory> transport_factory);
		};

		//////////////////////////////////////////////////////////////////////

		class ThreadedServer : public BaseServer
		{
		protected:
			vector<shared_ptr<boost::thread> > threads;

			virtual void serve_client(shared_ptr<BaseProcessor> proc);

		public:
			ThreadedServer(IProcessorFactory& processor_factory, shared_ptr<ITransportFactory> transport_factory);
		};

		//////////////////////////////////////////////////////////////////////

		class LibraryModeServer : public BaseServer
		{
		protected:
			virtual void serve_client(shared_ptr<BaseProcessor> proc);

		public:
			LibraryModeServer(IProcessorFactory& processor_factory);
			LibraryModeServer(IProcessorFactory& processor_factory, shared_ptr<SocketTransportFactory> transport_factory);
			virtual void serve();
		};

		//////////////////////////////////////////////////////////////////////

		class CmdlineServer
		{
		protected:
			IProcessorFactory& processor_factory;

		public:
			CmdlineServer(IProcessorFactory& processor_factory);
			int main(int argc, const char* argv[]);
		};


	}
}



#endif // AGNOS_SERVERS_HPP_INCLUDED
