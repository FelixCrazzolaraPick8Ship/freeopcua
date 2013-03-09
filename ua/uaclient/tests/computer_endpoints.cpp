/// @author Alexander Rykovanov 2012
/// @email rykovanov.as@gmail.com
/// @brief Test Remote computer connection.
/// @license GNU LGPL
///
/// Distributed under the GNU LGPL License
/// (See accompanying file LICENSE or copy at 
/// http://www.gnu.org/licenses/lgpl.html)
///

#include "common.h"

#include <opc/ua/client/computer.h>

#include <stdexcept>

using namespace OpcUa;
using namespace OpcUa::Remote;

class Endpoints : public ::testing::Test
{
protected:
  virtual void SetUp()
  {
    std::unique_ptr<OpcUa::Remote::Computer> computer = OpcUa::Remote::Connect(GetEndpoint());
    Server = computer->Endpoints();
  }

  virtual void TearDown()
  {
    Server = std::unique_ptr<EndpointServices>();
  }

protected:
  std::shared_ptr<EndpointServices> Server;
};


TEST_F(Endpoints, GetEndpoints)
{
  EndpointFilter filter;
  const std::vector<EndpointDescription> endpoints = Server->GetEndpoints(filter);
  ASSERT_FALSE(endpoints.empty());
}

